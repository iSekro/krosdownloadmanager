"""
Multi-threaded download engine with pause/resume, speed limiting,
and chunk-based downloading similar to Internet Download Manager.
"""

import hashlib
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional
from urllib.parse import unquote, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from krosdownloadmanager.utils.url_resolver import needs_resolution, resolve_url

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    MERGING = "merging"
    CANCELLED = "cancelled"


@dataclass
class DownloadSegment:
    index: int
    start: int
    end: int
    downloaded: int = 0
    completed: bool = False
    temp_file: str = ""


@dataclass
class DownloadItem:
    url: str
    save_path: str
    filename: str
    file_size: int = 0
    downloaded_bytes: int = 0
    status: DownloadStatus = DownloadStatus.QUEUED
    num_connections: int = 8
    segments: list = field(default_factory=list)
    speed: float = 0.0
    eta: str = "--:--"
    error_message: str = ""
    supports_resume: bool = False
    content_type: str = ""
    date_added: str = ""
    date_completed: str = ""
    checksum_md5: str = ""
    checksum_sha256: str = ""
    progress: float = 0.0
    speed_limit: int = 0  # bytes/s, 0 = unlimited
    scheduled_time: str = ""  # ISO format, empty = immediate
    priority: int = 0  # higher = more priority

    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.url}_{self.save_path}_{self.filename}".encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "save_path": self.save_path,
            "filename": self.filename,
            "file_size": self.file_size,
            "downloaded_bytes": self.downloaded_bytes,
            "status": self.status.value,
            "num_connections": self.num_connections,
            "supports_resume": self.supports_resume,
            "content_type": self.content_type,
            "date_added": self.date_added,
            "date_completed": self.date_completed,
            "progress": self.progress,
            "speed_limit": self.speed_limit,
            "checksum_md5": self.checksum_md5,
            "checksum_sha256": self.checksum_sha256,
            "scheduled_time": self.scheduled_time,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DownloadItem":
        item = cls(
            url=data["url"],
            save_path=str(data.get("save_path", "")),
            filename=str(data.get("filename", "")),
            file_size=data.get("file_size", 0),
            downloaded_bytes=data.get("downloaded_bytes", 0),
            status=DownloadStatus(data.get("status", "queued")),
            num_connections=data.get("num_connections", 8),
            supports_resume=data.get("supports_resume", False),
            content_type=data.get("content_type", ""),
            date_added=data.get("date_added", ""),
            date_completed=data.get("date_completed", ""),
            progress=data.get("progress", 0.0),
            speed_limit=data.get("speed_limit", 0),
            checksum_md5=data.get("checksum_md5", ""),
            checksum_sha256=data.get("checksum_sha256", ""),
            scheduled_time=data.get("scheduled_time", ""),
            priority=data.get("priority", 0),
        )
        return item


def _parse_content_disposition(cd: str) -> str:
    """Parse Content-Disposition header (RFC 6266 / RFC 5987)."""
    import re as _re

    # RFC 5987: filename*=UTF-8''encoded_name (takes priority)
    match = _re.search(r"filename\*\s*=\s*(?:UTF-8|utf-8)''(.+?)(?:;|$)", cd)
    if match:
        from urllib.parse import unquote as _unquote
        return _unquote(match.group(1).strip())

    # Standard: filename="name" or filename=name
    match = _re.search(r'filename\s*=\s*"([^"]+)"', cd)
    if match:
        return match.group(1).strip()
    match = _re.search(r"filename\s*=\s*([^;\s]+)", cd)
    if match:
        return match.group(1).strip().strip("'\"")

    return ""


def extract_filename_from_url(url: str, response: Optional[requests.Response] = None) -> str:
    if response and "Content-Disposition" in response.headers:
        fname = _parse_content_disposition(response.headers["Content-Disposition"])
        if fname:
            return fname

    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)

    if not filename or "." not in filename:
        filename = "download"

    return filename


class DownloadEngine:
    """Multi-threaded download engine with pause/resume support."""

    CHUNK_SIZE = 8192
    USER_AGENT = "KrosDownloadManager/1.0"
    MAX_RETRIES = 5
    RETRY_DELAY = 2

    def __init__(
        self,
        temp_dir: str = "",
        max_concurrent_downloads: int = 3,
        default_connections: int = 8,
        speed_limit: int = 0,
        proxy: str = "",
    ):
        self.temp_dir = temp_dir or os.path.join(os.path.expanduser("~"), ".krosdownloadmanager", "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.max_concurrent = max_concurrent_downloads
        self.default_connections = default_connections
        self.global_speed_limit = speed_limit
        self.proxy = proxy

        self.downloads: dict[str, DownloadItem] = {}
        self._stop_events: dict[str, threading.Event] = {}
        self._pause_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self._download_pool = ThreadPoolExecutor(max_workers=max_concurrent_downloads)
        self._active_futures: dict[str, object] = {}
        self._scheduler_thread: Optional[threading.Thread] = None
        self._scheduler_stop = threading.Event()

        self.on_progress: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        self._cleanup_orphaned_temp()
        self._start_scheduler()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry and proxy support."""
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers["User-Agent"] = self.USER_AGENT
        session.headers["Accept-Encoding"] = "identity"
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        return session

    def _start_scheduler(self) -> None:
        """Start the background scheduler that checks for scheduled downloads."""
        def scheduler_loop():
            while not self._scheduler_stop.is_set():
                now = time.strftime("%Y-%m-%d %H:%M")
                for download_id, item in list(self.downloads.items()):
                    if (
                        item.status == DownloadStatus.QUEUED
                        and item.scheduled_time
                        and item.scheduled_time <= now
                    ):
                        item.scheduled_time = ""
                        self.start_download(download_id)
                self._scheduler_stop.wait(30)

        self._scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    def get_file_info(self, url: str) -> dict:
        """Fetch file info (size, resume support, filename) from URL."""
        session = self._create_session()
        try:
            resp = session.head(url, allow_redirects=True, timeout=15)
            if resp.status_code >= 400:
                resp = session.get(url, stream=True, allow_redirects=True, timeout=15)

            file_size = int(resp.headers.get("Content-Length", 0))
            accept_ranges = resp.headers.get("Accept-Ranges", "none").lower()
            supports_resume = accept_ranges == "bytes" and file_size > 0
            content_type = resp.headers.get("Content-Type", "application/octet-stream")
            filename = extract_filename_from_url(url, resp)

            return {
                "file_size": file_size,
                "supports_resume": supports_resume,
                "content_type": content_type,
                "filename": filename,
                "url": resp.url,
            }
        except requests.RequestException as e:
            logger.error("Failed to get file info for %s: %s", url, e)
            return {
                "file_size": 0,
                "supports_resume": False,
                "content_type": "",
                "filename": extract_filename_from_url(url),
                "url": url,
                "error": str(e),
            }
        finally:
            session.close()

    def add_download(
        self,
        url: str,
        save_path: str,
        filename: str = "",
        num_connections: int = 0,
        start_immediately: bool = True,
        speed_limit: int = 0,
    ) -> DownloadItem:
        """Add a new download to the queue."""
        resolved_filename = ""
        if needs_resolution(url):
            logger.info("Resolving indirect URL: %s", url)
            result = resolve_url(url, proxy=self.proxy)
            if result.get("resolved"):
                url = result["url"]
                resolved_filename = result.get("filename", "")
                logger.info("Resolved to direct URL: %s", url)
            elif result.get("error"):
                logger.warning("URL resolution failed: %s", result["error"])

        info = self.get_file_info(url)

        if not filename:
            filename = resolved_filename or info["filename"]

        actual_url = info.get("url", url)

        item = DownloadItem(
            url=actual_url,
            save_path=save_path,
            filename=filename,
            file_size=info["file_size"],
            supports_resume=info["supports_resume"],
            content_type=info["content_type"],
            num_connections=num_connections or self.default_connections,
            date_added=time.strftime("%Y-%m-%d %H:%M:%S"),
            speed_limit=speed_limit or self.global_speed_limit,
        )

        if not item.supports_resume or item.file_size == 0:
            item.num_connections = 1

        with self._lock:
            self.downloads[item.id] = item
            self._stop_events[item.id] = threading.Event()
            self._pause_events[item.id] = threading.Event()
            self._pause_events[item.id].set()  # not paused initially

        if start_immediately:
            self.start_download(item.id)

        return item

    def start_download(self, download_id: str) -> None:
        """Start or resume a download."""
        item = self.downloads.get(download_id)
        if not item:
            return

        if item.status == DownloadStatus.DOWNLOADING:
            return

        self._stop_events[download_id] = threading.Event()
        if download_id not in self._pause_events:
            self._pause_events[download_id] = threading.Event()
        self._pause_events[download_id].set()

        item.status = DownloadStatus.DOWNLOADING
        self._notify_status(item)

        future = self._download_pool.submit(self._download_worker, download_id)
        self._active_futures[download_id] = future

    def pause_download(self, download_id: str) -> None:
        """Pause a download."""
        item = self.downloads.get(download_id)
        if not item or item.status != DownloadStatus.DOWNLOADING:
            return

        self._pause_events[download_id].clear()
        item.status = DownloadStatus.PAUSED
        item.speed = 0.0
        item.eta = "--:--"
        self._notify_status(item)

    def resume_download(self, download_id: str) -> None:
        """Resume a paused download."""
        item = self.downloads.get(download_id)
        if not item:
            return

        if item.status == DownloadStatus.PAUSED:
            self._pause_events[download_id].set()
            item.status = DownloadStatus.DOWNLOADING
            self._notify_status(item)
        elif item.status in (DownloadStatus.ERROR, DownloadStatus.QUEUED):
            self.start_download(download_id)

    def cancel_download(self, download_id: str) -> None:
        """Cancel and remove a download."""
        item = self.downloads.get(download_id)
        if not item:
            return

        if download_id in self._stop_events:
            self._stop_events[download_id].set()
        if download_id in self._pause_events:
            self._pause_events[download_id].set()

        item.status = DownloadStatus.CANCELLED
        item.speed = 0.0
        self._notify_status(item)

        self._cleanup_temp_files(download_id)

    def remove_download(self, download_id: str, delete_file: bool = False) -> None:
        """Remove a download from the list."""
        self.cancel_download(download_id)

        item = self.downloads.get(download_id)
        if item and delete_file:
            filepath = os.path.join(item.save_path, item.filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass

        with self._lock:
            self.downloads.pop(download_id, None)
            self._stop_events.pop(download_id, None)
            self._pause_events.pop(download_id, None)
            self._active_futures.pop(download_id, None)

    def _download_worker(self, download_id: str) -> None:
        """Main download worker - handles multi-segment downloading."""
        item = self.downloads.get(download_id)
        if not item:
            return

        os.makedirs(item.save_path, exist_ok=True)
        temp_dir = os.path.join(self.temp_dir, download_id)
        os.makedirs(temp_dir, exist_ok=True)

        try:
            if item.num_connections > 1 and item.supports_resume and item.file_size > 0:
                self._multi_segment_download(item, temp_dir)
            else:
                self._single_connection_download(item, temp_dir)
        except Exception as e:
            if not self._stop_events[download_id].is_set():
                item.status = DownloadStatus.ERROR
                item.error_message = str(e)
                item.speed = 0.0
                logger.error("Download failed for %s: %s", item.filename, e)
                self._notify_status(item)
                if self.on_error:
                    self.on_error(item)

    def _single_connection_download(self, item: DownloadItem, temp_dir: str) -> None:
        """Download with a single connection and exponential backoff retry."""
        stop_event = self._stop_events[item.id]
        pause_event = self._pause_events[item.id]
        session = self._create_session()
        temp_file = os.path.join(temp_dir, f"{item.filename}.part")

        retries = 0
        while retries < self.MAX_RETRIES and not stop_event.is_set():
            try:
                headers: dict[str, str] = {}
                mode = "ab"
                existing_size = 0

                if os.path.exists(temp_file):
                    existing_size = os.path.getsize(temp_file)
                    if item.supports_resume and existing_size > 0:
                        headers["Range"] = f"bytes={existing_size}-"
                        item.downloaded_bytes = existing_size

                resp = session.get(item.url, headers=headers, stream=True, timeout=30)
                if resp.status_code == 416:
                    item.downloaded_bytes = item.file_size
                    item.progress = 100.0
                    self._finalize_download(item, temp_file)
                    return

                resp.raise_for_status()

                if item.file_size == 0:
                    item.file_size = int(resp.headers.get("Content-Length", 0)) + existing_size

                speed_tracker = _SpeedTracker()

                with open(temp_file, mode) as f:
                    for chunk in resp.iter_content(chunk_size=self.CHUNK_SIZE):
                        if stop_event.is_set():
                            return

                        pause_event.wait()

                        if stop_event.is_set():
                            return

                        if chunk:
                            f.write(chunk)
                            chunk_len = len(chunk)
                            item.downloaded_bytes += chunk_len
                            speed_tracker.add(chunk_len)

                            if item.file_size > 0:
                                item.progress = (item.downloaded_bytes / item.file_size) * 100

                            item.speed = speed_tracker.speed
                            item.eta = self._calculate_eta(item)
                            self._notify_progress(item)

                            if item.speed_limit > 0:
                                self._apply_speed_limit(item.speed_limit, speed_tracker)

                self._finalize_download(item, temp_file)
                return

            except requests.RequestException as e:
                retries += 1
                if retries >= self.MAX_RETRIES:
                    raise RuntimeError(f"Download failed after {self.MAX_RETRIES} retries: {e}") from e
                delay = self.RETRY_DELAY * (2 ** (retries - 1))  # exponential backoff
                logger.warning(
                    "Retry %d/%d for %s (waiting %.1fs): %s",
                    retries, self.MAX_RETRIES, item.filename, delay, e,
                )
                time.sleep(delay)
            finally:
                session.close()

    def _multi_segment_download(self, item: DownloadItem, temp_dir: str) -> None:
        """Download with multiple connections (segments)."""
        stop_event = self._stop_events[item.id]
        pause_event = self._pause_events[item.id]

        segment_size = item.file_size // item.num_connections
        segments = []

        for i in range(item.num_connections):
            start = i * segment_size
            end = item.file_size - 1 if i == item.num_connections - 1 else (i + 1) * segment_size - 1
            seg_file = os.path.join(temp_dir, f"segment_{i}.part")

            seg = DownloadSegment(
                index=i,
                start=start,
                end=end,
                temp_file=seg_file,
            )

            if os.path.exists(seg_file):
                existing = os.path.getsize(seg_file)
                seg.downloaded = existing
                seg.start += existing
                if seg.start > seg.end:
                    seg.completed = True

            segments.append(seg)

        item.segments = segments
        item.downloaded_bytes = sum(s.downloaded for s in segments)

        speed_tracker = _SpeedTracker()
        segment_lock = threading.Lock()

        session = self._create_session()

        def download_segment(seg: DownloadSegment) -> None:
            if seg.completed or stop_event.is_set():
                return

            headers = {
                "Range": f"bytes={seg.start}-{seg.end}",
                "Accept-Encoding": "identity",
            }

            retries = 0
            while retries < self.MAX_RETRIES and not stop_event.is_set():
                try:
                    resp = session.get(item.url, headers=headers, stream=True, timeout=30)
                    resp.raise_for_status()

                    with open(seg.temp_file, "ab") as f:
                        for chunk in resp.iter_content(chunk_size=self.CHUNK_SIZE):
                            if stop_event.is_set():
                                return

                            pause_event.wait()
                            if stop_event.is_set():
                                return

                            if chunk:
                                f.write(chunk)
                                chunk_len = len(chunk)
                                seg.downloaded += chunk_len

                                with segment_lock:
                                    item.downloaded_bytes += chunk_len
                                    speed_tracker.add(chunk_len)

                                    if item.file_size > 0:
                                        item.progress = (item.downloaded_bytes / item.file_size) * 100

                                    item.speed = speed_tracker.speed
                                    item.eta = self._calculate_eta(item)
                                    self._notify_progress(item)

                                if item.speed_limit > 0:
                                    per_seg_limit = item.speed_limit // max(1, item.num_connections)
                                    self._apply_speed_limit(per_seg_limit, speed_tracker)

                    seg.completed = True
                    return

                except requests.RequestException as e:
                    retries += 1
                    if retries >= self.MAX_RETRIES:
                        raise RuntimeError(f"Segment {seg.index} failed after {self.MAX_RETRIES} retries: {e}") from e
                    time.sleep(self.RETRY_DELAY * retries)
                    headers["Range"] = f"bytes={seg.start + seg.downloaded}-{seg.end}"

        try:
            with ThreadPoolExecutor(max_workers=item.num_connections) as pool:
                futures = {pool.submit(download_segment, seg): seg for seg in segments if not seg.completed}
                for future in as_completed(futures):
                    if stop_event.is_set():
                        return
                    future.result()
        finally:
            session.close()

        if stop_event.is_set():
            return

        item.status = DownloadStatus.MERGING
        self._notify_status(item)

        output_path = os.path.join(temp_dir, item.filename)
        with open(output_path, "wb") as outfile:
            for seg in sorted(segments, key=lambda s: s.index):
                with open(seg.temp_file, "rb") as seg_file:
                    while True:
                        chunk = seg_file.read(self.CHUNK_SIZE * 4)
                        if not chunk:
                            break
                        outfile.write(chunk)

        self._finalize_download(item, output_path)

    def _finalize_download(self, item: DownloadItem, temp_path: str) -> None:
        """Move temp file to final location, compute checksums, and clean up."""
        final_path = os.path.join(item.save_path, item.filename)

        if os.path.exists(final_path):
            base, ext = os.path.splitext(item.filename)
            counter = 1
            while os.path.exists(final_path):
                final_path = os.path.join(item.save_path, f"{base} ({counter}){ext}")
                counter += 1
            item.filename = os.path.basename(final_path)

        import shutil
        shutil.move(temp_path, final_path)

        item.status = DownloadStatus.COMPLETED
        item.progress = 100.0
        item.speed = 0.0
        item.eta = "00:00"
        item.date_completed = time.strftime("%Y-%m-%d %H:%M:%S")
        item.downloaded_bytes = item.file_size if item.file_size > 0 else os.path.getsize(final_path)
        if item.file_size == 0:
            item.file_size = item.downloaded_bytes

        self._compute_checksums(item, final_path)

        self._notify_status(item)
        self._notify_progress(item)

        if self.on_complete:
            self.on_complete(item)

        self._cleanup_temp_files(item.id)

    def _compute_checksums(self, item: DownloadItem, file_path: str) -> None:
        """Compute MD5 and SHA-256 checksums for a completed download."""
        try:
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE * 8)
                    if not chunk:
                        break
                    md5.update(chunk)
                    sha256.update(chunk)
            item.checksum_md5 = md5.hexdigest()
            item.checksum_sha256 = sha256.hexdigest()
            logger.info("Checksums for %s: MD5=%s SHA256=%s", item.filename, item.checksum_md5, item.checksum_sha256)
        except OSError as e:
            logger.warning("Failed to compute checksums for %s: %s", item.filename, e)

    def _cleanup_orphaned_temp(self) -> None:
        """Remove temp dirs that don't belong to any tracked download on startup."""
        if not os.path.isdir(self.temp_dir):
            return
        import shutil
        known_ids = set(self.downloads.keys())
        for entry in os.listdir(self.temp_dir):
            if entry not in known_ids:
                path = os.path.join(self.temp_dir, entry)
                if os.path.isdir(path):
                    try:
                        shutil.rmtree(path)
                        logger.debug("Cleaned orphaned temp dir: %s", entry)
                    except OSError:
                        pass

    def _cleanup_temp_files(self, download_id: str) -> None:
        """Remove temp files for a download."""
        temp_dir = os.path.join(self.temp_dir, download_id)
        if os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass

    def _calculate_eta(self, item: DownloadItem) -> str:
        """Calculate estimated time remaining."""
        if item.speed <= 0 or item.file_size <= 0:
            return "--:--"

        remaining = item.file_size - item.downloaded_bytes
        if remaining <= 0:
            return "00:00"

        seconds = remaining / item.speed
        if seconds > 86400:
            return f"{int(seconds / 86400)}d {int((seconds % 86400) / 3600)}h"
        elif seconds > 3600:
            return f"{int(seconds / 3600)}h {int((seconds % 3600) / 60)}m"
        else:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"

    def _apply_speed_limit(self, limit: int, tracker: "_SpeedTracker") -> None:
        """Throttle download speed if exceeding limit."""
        if limit <= 0:
            return
        if tracker.speed > limit:
            sleep_time = (tracker.speed - limit) / limit * 0.1
            time.sleep(min(sleep_time, 1.0))

    def _notify_progress(self, item: DownloadItem) -> None:
        if self.on_progress:
            try:
                self.on_progress(item)
            except Exception:
                pass

    def _notify_status(self, item: DownloadItem) -> None:
        if self.on_status_change:
            try:
                self.on_status_change(item)
            except Exception:
                pass

    def get_all_downloads(self) -> list[DownloadItem]:
        return list(self.downloads.values())

    def shutdown(self) -> None:
        """Stop all downloads and clean up."""
        self._scheduler_stop.set()

        for download_id in list(self._stop_events.keys()):
            if download_id in self._stop_events:
                self._stop_events[download_id].set()
            if download_id in self._pause_events:
                self._pause_events[download_id].set()

        self._download_pool.shutdown(wait=False)


class _SpeedTracker:
    """Track download speed using a sliding window."""

    def __init__(self, window_size: float = 2.0):
        self._lock = threading.Lock()
        self._samples: list[tuple[float, int]] = []
        self._window_size = window_size
        self.speed: float = 0.0

    def add(self, byte_count: int) -> None:
        now = time.monotonic()
        with self._lock:
            self._samples.append((now, byte_count))
            cutoff = now - self._window_size
            self._samples = [(t, b) for t, b in self._samples if t > cutoff]

            if len(self._samples) >= 2:
                time_span = self._samples[-1][0] - self._samples[0][0]
                if time_span > 0:
                    total_bytes = sum(b for _, b in self._samples)
                    self.speed = total_bytes / time_span
