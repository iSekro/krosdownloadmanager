"""Local HTTP API server for browser extension communication."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _APIHandler(BaseHTTPRequestHandler):
    """Handler for extension API requests."""

    app = None

    def log_message(self, format, *args):
        pass

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status, data):
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            active = 0
            total = 0
            if self.app and hasattr(self.app, "engine"):
                from krosdownloadmanager.core.download_engine import DownloadStatus
                for item in self.app.engine.downloads.values():
                    total += 1
                    if item.status == DownloadStatus.DOWNLOADING:
                        active += 1
            self._send_json(200, {
                "status": "running",
                "version": "1.0",
                "active_downloads": active,
                "total_downloads": total,
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/download":
            data = self._read_body()
            if data is None:
                self.send_response(400)
                self.end_headers()
                return

            url = data.get("url", "")
            if not url:
                self._send_json(400, {"error": "URL required"})
                return

            self._send_json(200, {"queued": True})

            if self.app:
                self.app.after(0, lambda: self.app.add_download_from_extension(url))

        elif self.path == "/download_batch":
            data = self._read_body()
            if data is None:
                self.send_response(400)
                self.end_headers()
                return

            urls = data.get("urls", [])
            if not urls:
                self._send_json(400, {"error": "URLs required"})
                return

            self._send_json(200, {"queued": True, "count": len(urls)})

            if self.app:
                for item in urls:
                    url = item.get("url", "") if isinstance(item, dict) else item
                    if url:
                        self.app.after(0, lambda u=url: self.app.add_download_from_extension(u))

        elif self.path == "/file_info":
            data = self._read_body()
            if data is None:
                self.send_response(400)
                self.end_headers()
                return

            url = data.get("url", "")
            if not url:
                self._send_json(400, {"error": "URL required"})
                return

            info = {}
            if self.app and hasattr(self.app, "engine"):
                info = self.app.engine.get_file_info(url)

            self._send_json(200, {
                "filename": info.get("filename", ""),
                "file_size": info.get("file_size", 0),
                "content_type": info.get("content_type", ""),
                "supports_resume": info.get("supports_resume", False),
            })
        else:
            self.send_response(404)
            self.end_headers()


class ExtensionAPIServer:
    """Runs a local HTTP server for browser extension communication."""

    def __init__(self, app, port: int = 29256):
        self.app = app
        self.port = port
        self._server = None
        self._thread = None

    def start(self) -> None:
        _APIHandler.app = self.app
        try:
            self._server = HTTPServer(("127.0.0.1", self.port), _APIHandler)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
        except OSError:
            pass

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
