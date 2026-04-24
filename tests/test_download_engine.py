"""Tests for the download engine."""

import os
import tempfile

from krosdownloadmanager.core.download_engine import (
    DownloadItem,
    DownloadStatus,
    extract_filename_from_url,
)
from krosdownloadmanager.core.config import AppConfig, ConfigManager


def test_download_item_creation():
    item = DownloadItem(
        url="https://example.com/file.zip",
        save_path="/tmp/downloads",
        filename="file.zip",
        file_size=1024 * 1024,
    )
    assert item.filename == "file.zip"
    assert item.status == DownloadStatus.QUEUED
    assert item.progress == 0.0


def test_download_item_id():
    item = DownloadItem(
        url="https://example.com/file.zip",
        save_path="/tmp/downloads",
        filename="file.zip",
    )
    assert len(item.id) == 12


def test_download_item_serialization():
    item = DownloadItem(
        url="https://example.com/file.zip",
        save_path="/tmp/downloads",
        filename="file.zip",
        file_size=1024,
        status=DownloadStatus.COMPLETED,
    )
    data = item.to_dict()
    assert data["url"] == "https://example.com/file.zip"
    assert data["status"] == "completed"

    restored = DownloadItem.from_dict(data)
    assert restored.url == item.url
    assert restored.status == DownloadStatus.COMPLETED


def test_download_item_serialization_with_checksums():
    item = DownloadItem(
        url="https://example.com/file.zip",
        save_path="/tmp/downloads",
        filename="file.zip",
        file_size=1024,
        status=DownloadStatus.COMPLETED,
        checksum_md5="d41d8cd98f00b204e9800998ecf8427e",
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    data = item.to_dict()
    assert data["checksum_md5"] == "d41d8cd98f00b204e9800998ecf8427e"
    assert data["checksum_sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    restored = DownloadItem.from_dict(data)
    assert restored.checksum_md5 == item.checksum_md5
    assert restored.checksum_sha256 == item.checksum_sha256


def test_download_item_with_schedule():
    item = DownloadItem(
        url="https://example.com/file.zip",
        save_path="/tmp/downloads",
        filename="file.zip",
        scheduled_time="2025-12-31 23:00",
        priority=5,
    )
    data = item.to_dict()
    assert data["scheduled_time"] == "2025-12-31 23:00"
    assert data["priority"] == 5

    restored = DownloadItem.from_dict(data)
    assert restored.scheduled_time == "2025-12-31 23:00"
    assert restored.priority == 5


def test_extract_filename_from_url():
    assert extract_filename_from_url("https://example.com/file.zip") == "file.zip"
    assert extract_filename_from_url("https://example.com/path/to/document.pdf") == "document.pdf"
    assert extract_filename_from_url("https://example.com/") == "download"


def test_app_config_defaults():
    config = AppConfig()
    assert config.max_concurrent_downloads == 3
    assert config.default_connections == 8
    assert config.speed_limit == 0
    assert config.theme == "dark"
    assert "Downloads" in config.download_dir
    assert config.proxy == ""
    assert config.proxy_enabled is False


def test_config_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(config_dir=tmpdir)
        manager.config.default_connections = 16
        manager.config.speed_limit = 1024 * 100
        manager.save_config()

        manager2 = ConfigManager(config_dir=tmpdir)
        assert manager2.config.default_connections == 16
        assert manager2.config.speed_limit == 1024 * 100


def test_config_manager_proxy():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(config_dir=tmpdir)
        manager.config.proxy = "http://proxy:8080"
        manager.config.proxy_enabled = True
        manager.save_config()

        manager2 = ConfigManager(config_dir=tmpdir)
        assert manager2.config.proxy == "http://proxy:8080"
        assert manager2.config.proxy_enabled is True


def test_config_manager_downloads():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(config_dir=tmpdir)

        downloads = [
            {"url": "https://example.com/file1.zip", "filename": "file1.zip",
             "save_path": "/tmp", "status": "completed"},
            {"url": "https://example.com/file2.exe", "filename": "file2.exe",
             "save_path": "/tmp", "status": "paused"},
        ]
        manager.save_downloads(downloads)

        loaded = manager.load_downloads()
        assert len(loaded) == 2
        assert loaded[0]["filename"] == "file1.zip"
