"""
URL resolver for file hosting services.

Resolves indirect download links (e.g., MediaFire, Google Drive, Dropbox,
SourceForge, YouTube) into direct download URLs so the download engine can
fetch the actual file instead of an HTML page.
"""

import logging
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
import yt_dlp

logger = logging.getLogger(__name__)

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _make_session(proxy: str = "") -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = _BROWSER_UA
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    return session


def _is_html_response(resp: requests.Response) -> bool:
    ct = resp.headers.get("Content-Type", "")
    return "text/html" in ct or "application/xhtml" in ct


# ---------------------------------------------------------------------------
# MediaFire
# ---------------------------------------------------------------------------

_MEDIAFIRE_PATTERNS = [
    re.compile(r'https?://www\.mediafire\.com/file/'),
    re.compile(r'https?://mediafire\.com/file/'),
    re.compile(r'https?://www\.mediafire\.com/\?'),
    re.compile(r'https?://mediafire\.com/\?'),
]

_MF_DIRECT_RE = re.compile(
    r'href="(https?://download\d*\.mediafire\.com/[^"]+)"',
    re.IGNORECASE,
)

_MF_ARIA_RE = re.compile(
    r'aria-label="Download file"\s+href="(https?://[^"]+)"',
    re.IGNORECASE,
)

_MF_DL_BTN_RE = re.compile(
    r'id="downloadButton"[^>]*href="(https?://[^"]+)"',
    re.IGNORECASE,
)

_MF_DL_BTN_RE2 = re.compile(
    r'href="(https?://[^"]+)"[^>]*id="downloadButton"',
    re.IGNORECASE,
)


def _is_mediafire(url: str) -> bool:
    return any(p.search(url) for p in _MEDIAFIRE_PATTERNS)


def _resolve_mediafire(url: str, proxy: str = "") -> dict:
    """Resolve a MediaFire page URL to a direct download link."""
    session = _make_session(proxy)
    try:
        resp = session.get(url, allow_redirects=True, timeout=20)
        resp.raise_for_status()

        html = resp.text

        for pattern in (_MF_DIRECT_RE, _MF_ARIA_RE, _MF_DL_BTN_RE, _MF_DL_BTN_RE2):
            match = pattern.search(html)
            if match:
                direct_url = match.group(1)
                logger.info("MediaFire resolved: %s -> %s", url, direct_url)

                filename_match = re.search(
                    r'<div\s+class="filename">([^<]+)</div>', html
                )
                filename = filename_match.group(1).strip() if filename_match else ""

                return {"url": direct_url, "filename": filename, "resolved": True}

        logger.warning("MediaFire page found but no download link extracted: %s", url)
        return {"url": url, "filename": "", "resolved": False, "error": "No se encontró el enlace de descarga en la página de MediaFire"}
    except requests.RequestException as e:
        logger.error("Failed to resolve MediaFire URL %s: %s", url, e)
        return {"url": url, "filename": "", "resolved": False, "error": str(e)}
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Google Drive
# ---------------------------------------------------------------------------

_GDRIVE_FILE_RE = re.compile(
    r'https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
)
_GDRIVE_OPEN_RE = re.compile(
    r'https?://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
)
_GDRIVE_UC_RE = re.compile(
    r'https?://drive\.google\.com/uc\?',
)


def _is_google_drive(url: str) -> bool:
    return bool(_GDRIVE_FILE_RE.search(url) or _GDRIVE_OPEN_RE.search(url) or _GDRIVE_UC_RE.search(url))


def _resolve_google_drive(url: str, proxy: str = "") -> dict:
    """Convert Google Drive share URL to direct download URL."""
    file_id = ""

    match = _GDRIVE_FILE_RE.search(url)
    if match:
        file_id = match.group(1)

    if not file_id:
        match = _GDRIVE_OPEN_RE.search(url)
        if match:
            file_id = match.group(1)

    if not file_id:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        file_id = qs.get("id", [""])[0]

    if file_id:
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
        logger.info("Google Drive resolved: %s -> %s", url, direct_url)
        return {"url": direct_url, "filename": "", "resolved": True}

    return {"url": url, "filename": "", "resolved": False, "error": "No se pudo extraer el ID del archivo de Google Drive"}


# ---------------------------------------------------------------------------
# Dropbox
# ---------------------------------------------------------------------------

def _is_dropbox(url: str) -> bool:
    return "dropbox.com/" in url and ("/s/" in url or "/scl/" in url)


def _resolve_dropbox(url: str, proxy: str = "") -> dict:
    """Convert Dropbox share URL to direct download URL."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs["dl"] = ["1"]
    new_query = urlencode(qs, doseq=True)
    direct_url = urlunparse(parsed._replace(query=new_query))
    logger.info("Dropbox resolved: %s -> %s", url, direct_url)
    return {"url": direct_url, "filename": "", "resolved": True}


# ---------------------------------------------------------------------------
# SourceForge
# ---------------------------------------------------------------------------

_SF_RE = re.compile(r'https?://sourceforge\.net/projects/[^/]+/files/')


def _is_sourceforge(url: str) -> bool:
    return bool(_SF_RE.search(url))


def _resolve_sourceforge(url: str, proxy: str = "") -> dict:
    """Ensure SourceForge URL uses the direct download suffix."""
    if not url.endswith("/download"):
        direct_url = url.rstrip("/") + "/download"
    else:
        direct_url = url
    logger.info("SourceForge resolved: %s -> %s", url, direct_url)
    return {"url": direct_url, "filename": "", "resolved": True}


# ---------------------------------------------------------------------------
# YouTube (via yt-dlp)
# ---------------------------------------------------------------------------

_YOUTUBE_PATTERNS = [
    re.compile(r'https?://(www\.)?youtube\.com/watch\?'),
    re.compile(r'https?://(www\.)?youtube\.com/shorts/'),
    re.compile(r'https?://youtu\.be/'),
    re.compile(r'https?://(www\.)?youtube\.com/embed/'),
    re.compile(r'https?://m\.youtube\.com/watch\?'),
]


def _is_youtube(url: str) -> bool:
    return any(p.search(url) for p in _YOUTUBE_PATTERNS)


def _resolve_youtube(url: str, proxy: str = "") -> dict:
    """Extract best direct video URL from YouTube using yt-dlp."""
    ydl_opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "skip_download": True,
    }
    if proxy:
        ydl_opts["proxy"] = proxy

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {"url": url, "filename": "", "resolved": False,
                        "error": "yt-dlp returned no info"}

            direct_url = info.get("url", "")
            if not direct_url:
                formats = info.get("formats", [])
                if formats:
                    best = formats[-1]
                    direct_url = best.get("url", "")

            if not direct_url:
                return {"url": url, "filename": "", "resolved": False,
                        "error": "Could not extract video URL"}

            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
            filename = f"{title}.{ext}"
            # Sanitize filename
            filename = re.sub(r'[\\/:*?"<>|]', "_", filename)

            logger.info("YouTube resolved: %s -> %s", url, direct_url[:80])
            return {"url": direct_url, "filename": filename, "resolved": True}

    except Exception as exc:
        logger.error("Failed to resolve YouTube URL %s: %s", url, exc)
        return {"url": url, "filename": "", "resolved": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Generic redirect resolver
# ---------------------------------------------------------------------------

def _resolve_generic(url: str, proxy: str = "") -> dict:
    """Follow redirects and check if the final URL is a file, not HTML."""
    session = _make_session(proxy)
    try:
        resp = session.head(url, allow_redirects=True, timeout=15)
        final_url = resp.url

        if final_url != url:
            if not _is_html_response(resp):
                logger.info("Generic redirect resolved: %s -> %s", url, final_url)
                return {"url": final_url, "filename": "", "resolved": True}

        resp_get = session.get(url, stream=True, allow_redirects=True, timeout=15)
        final_url = resp_get.url

        if not _is_html_response(resp_get):
            logger.info("Generic GET resolved: %s -> %s", url, final_url)
            resp_get.close()
            return {"url": final_url, "filename": "", "resolved": True}

        resp_get.close()
        return {"url": url, "filename": "", "resolved": False}
    except requests.RequestException:
        return {"url": url, "filename": "", "resolved": False}
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_RESOLVERS = [
    (_is_youtube, _resolve_youtube),
    (_is_mediafire, _resolve_mediafire),
    (_is_google_drive, _resolve_google_drive),
    (_is_dropbox, _resolve_dropbox),
    (_is_sourceforge, _resolve_sourceforge),
]


def resolve_url(url: str, proxy: str = "") -> dict:
    """
    Resolve a URL to a direct download link.

    Returns a dict with:
      - url: the resolved (or original) URL
      - filename: extracted filename if available
      - resolved: True if URL was resolved to a direct link
      - error: error message if resolution failed (optional)
    """
    for detector, resolver in _RESOLVERS:
        if detector(url):
            result = resolver(url, proxy)
            if result.get("resolved"):
                return result
            return result

    return {"url": url, "filename": "", "resolved": False}


def needs_resolution(url: str) -> bool:
    """Check if a URL is from a known file hosting service that needs resolution."""
    return any(detector(url) for detector, _ in _RESOLVERS)
