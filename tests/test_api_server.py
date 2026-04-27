"""Tests for the extension API server."""

import json
import time
import urllib.request

from krosdownloadmanager.core.api_server import ExtensionAPIServer


class FakeApp:
    """Fake app for testing."""

    def __init__(self):
        self.last_url = None
        self.all_urls = []

    def after(self, ms, func):
        func()

    def add_download_from_extension(self, url):
        self.last_url = url
        self.all_urls.append(url)


def test_status_endpoint():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39256)
    server.start()
    time.sleep(0.3)
    try:
        req = urllib.request.Request("http://127.0.0.1:39256/status")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            assert data["status"] == "running"
            assert data["version"] == "1.0"
            assert "active_downloads" in data
            assert "total_downloads" in data
    finally:
        server.stop()


def test_download_endpoint():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39257)
    server.start()
    time.sleep(0.3)
    try:
        body = json.dumps({"url": "https://example.com/file.zip"}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:39257/download",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            assert data["queued"] is True
    finally:
        server.stop()


def test_download_batch_endpoint():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39260)
    server.start()
    time.sleep(0.3)
    try:
        urls = [
            {"url": "https://example.com/file1.zip", "filename": "file1.zip"},
            {"url": "https://example.com/file2.zip", "filename": "file2.zip"},
        ]
        body = json.dumps({"urls": urls}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:39260/download_batch",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            assert data["queued"] is True
            assert data["count"] == 2
    finally:
        server.stop()


def test_download_no_url():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39258)
    server.start()
    time.sleep(0.3)
    try:
        body = json.dumps({"url": ""}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:39258/download",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=2)
            assert False, "Should have returned 400"
        except urllib.error.HTTPError as e:
            assert e.code == 400
    finally:
        server.stop()


def test_404_endpoint():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39259)
    server.start()
    time.sleep(0.3)
    try:
        req = urllib.request.Request("http://127.0.0.1:39259/nonexistent")
        try:
            urllib.request.urlopen(req, timeout=2)
            assert False, "Should have returned 404"
        except urllib.error.HTTPError as e:
            assert e.code == 404
    finally:
        server.stop()


def test_file_info_endpoint():
    app = FakeApp()
    server = ExtensionAPIServer(app, port=39261)
    server.start()
    time.sleep(0.3)
    try:
        body = json.dumps({"url": "https://example.com/test.zip"}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:39261/file_info",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            assert "filename" in data
            assert "file_size" in data
    finally:
        server.stop()
