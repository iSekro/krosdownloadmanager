"""Tests for the URL resolver module."""

from krosdownloadmanager.utils.url_resolver import (
    _is_dropbox,
    _is_google_drive,
    _is_mediafire,
    _is_sourceforge,
    _resolve_dropbox,
    _resolve_google_drive,
    _resolve_sourceforge,
    needs_resolution,
    resolve_url,
)


class TestNeedsResolution:
    def test_mediafire_url(self):
        assert needs_resolution("https://www.mediafire.com/file/abc123/test.zip/file")

    def test_google_drive_url(self):
        assert needs_resolution("https://drive.google.com/file/d/1234abc/view")

    def test_dropbox_url(self):
        assert needs_resolution("https://www.dropbox.com/s/abc123/file.zip?dl=0")

    def test_sourceforge_url(self):
        assert needs_resolution("https://sourceforge.net/projects/myproject/files/v1.0/app.exe")

    def test_direct_url(self):
        assert not needs_resolution("https://example.com/file.zip")

    def test_localhost_url(self):
        assert not needs_resolution("http://localhost:8888/test.bin")


class TestMediaFireDetection:
    def test_standard_url(self):
        assert _is_mediafire("https://www.mediafire.com/file/abc123/test.zip/file")

    def test_no_www(self):
        assert _is_mediafire("https://mediafire.com/file/abc123/test.zip/file")

    def test_old_format(self):
        assert _is_mediafire("https://www.mediafire.com/?abc123")

    def test_not_mediafire(self):
        assert not _is_mediafire("https://google.com/file/test.zip")


class TestGoogleDriveResolution:
    def test_file_d_format(self):
        assert _is_google_drive("https://drive.google.com/file/d/1abc_XYZ/view?usp=sharing")

    def test_open_format(self):
        assert _is_google_drive("https://drive.google.com/open?id=1abc_XYZ")

    def test_resolve_file_d(self):
        result = _resolve_google_drive("https://drive.google.com/file/d/1abc_XYZ/view?usp=sharing")
        assert result["resolved"]
        assert "1abc_XYZ" in result["url"]
        assert "export=download" in result["url"]

    def test_resolve_open(self):
        result = _resolve_google_drive("https://drive.google.com/open?id=1abc_XYZ")
        assert result["resolved"]
        assert "1abc_XYZ" in result["url"]

    def test_not_gdrive(self):
        assert not _is_google_drive("https://example.com/file.zip")


class TestDropboxResolution:
    def test_detect(self):
        assert _is_dropbox("https://www.dropbox.com/s/abc123/file.zip?dl=0")

    def test_detect_scl(self):
        assert _is_dropbox("https://www.dropbox.com/scl/fi/abc/file.zip?dl=0")

    def test_resolve(self):
        result = _resolve_dropbox("https://www.dropbox.com/s/abc123/file.zip?dl=0")
        assert result["resolved"]
        assert "dl=1" in result["url"]

    def test_not_dropbox(self):
        assert not _is_dropbox("https://example.com/file.zip")


class TestSourceForgeResolution:
    def test_detect(self):
        assert _is_sourceforge("https://sourceforge.net/projects/myproject/files/v1.0/app.exe")

    def test_resolve_adds_download(self):
        result = _resolve_sourceforge("https://sourceforge.net/projects/myproject/files/v1.0/app.exe")
        assert result["resolved"]
        assert result["url"].endswith("/download")

    def test_resolve_already_has_download(self):
        url = "https://sourceforge.net/projects/myproject/files/v1.0/app.exe/download"
        result = _resolve_sourceforge(url)
        assert result["resolved"]
        assert result["url"].endswith("/download")
        assert not result["url"].endswith("/download/download")

    def test_not_sourceforge(self):
        assert not _is_sourceforge("https://example.com/file.zip")


class TestResolveUrl:
    def test_direct_url_not_resolved(self):
        result = resolve_url("https://example.com/file.zip")
        assert not result["resolved"]
        assert result["url"] == "https://example.com/file.zip"

    def test_google_drive_resolved(self):
        result = resolve_url("https://drive.google.com/file/d/1abc_XYZ/view")
        assert result["resolved"]
        assert "export=download" in result["url"]

    def test_dropbox_resolved(self):
        result = resolve_url("https://www.dropbox.com/s/abc123/file.zip?dl=0")
        assert result["resolved"]
        assert "dl=1" in result["url"]

    def test_sourceforge_resolved(self):
        result = resolve_url("https://sourceforge.net/projects/mp/files/v1/a.exe")
        assert result["resolved"]
        assert result["url"].endswith("/download")
