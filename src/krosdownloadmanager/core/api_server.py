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

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {"status": "running", "version": "1.0"}
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/download":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_response(400)
                self.end_headers()
                return

            url = data.get("url", "")
            if not url:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "URL required"}).encode())
                return

            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"queued": True}).encode())

            if self.app:
                self.app.after(0, lambda: self.app.add_download_from_extension(url))
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
