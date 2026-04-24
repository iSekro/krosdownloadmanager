"""Configuration manager for KrosDownloadManager."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    download_dir: str = ""
    temp_dir: str = ""
    max_concurrent_downloads: int = 3
    default_connections: int = 8
    speed_limit: int = 0  # bytes/s, 0 = unlimited
    auto_start_downloads: bool = True
    show_notifications: bool = True
    minimize_to_tray: bool = True
    clipboard_monitoring: bool = True
    theme: str = "dark"
    language: str = "es"
    proxy: str = ""
    proxy_enabled: bool = False
    file_categories: dict = field(default_factory=lambda: {
        "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2"],
        "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"],
        "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
        "Music": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
        "Programs": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".apk", ".appimage"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
        "General": [],
    })
    window_width: int = 1100
    window_height: int = 700
    confirmed_extensions: list = field(default_factory=lambda: [
        ".exe", ".msi", ".zip", ".rar", ".7z", ".iso",
        ".mp4", ".mkv", ".avi", ".mp3", ".flac",
        ".pdf", ".doc", ".docx",
    ])

    def __post_init__(self):
        if not self.download_dir:
            self.download_dir = str(Path.home() / "Downloads" / "KrosDownloads")
        if not self.temp_dir:
            self.temp_dir = str(Path.home() / ".krosdownloadmanager" / "temp")


class ConfigManager:
    """Manages application configuration with persistent storage."""

    def __init__(self, config_dir: str = ""):
        if not config_dir:
            config_dir = str(Path.home() / ".krosdownloadmanager")

        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self.downloads_file = os.path.join(config_dir, "downloads.json")

        os.makedirs(config_dir, exist_ok=True)

        self.config = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from disk."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                config = AppConfig()
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                return config
            except (json.JSONDecodeError, OSError):
                pass
        return AppConfig()

    def save_config(self) -> None:
        """Save configuration to disk."""
        data = {
            "download_dir": self.config.download_dir,
            "temp_dir": self.config.temp_dir,
            "max_concurrent_downloads": self.config.max_concurrent_downloads,
            "default_connections": self.config.default_connections,
            "speed_limit": self.config.speed_limit,
            "auto_start_downloads": self.config.auto_start_downloads,
            "show_notifications": self.config.show_notifications,
            "minimize_to_tray": self.config.minimize_to_tray,
            "clipboard_monitoring": self.config.clipboard_monitoring,
            "theme": self.config.theme,
            "language": self.config.language,
            "window_width": self.config.window_width,
            "window_height": self.config.window_height,
            "proxy": self.config.proxy,
            "proxy_enabled": self.config.proxy_enabled,
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_downloads(self, downloads: list[dict]) -> None:
        """Save download list to disk."""
        with open(self.downloads_file, "w", encoding="utf-8") as f:
            json.dump(downloads, f, indent=2)

    def load_downloads(self) -> list[dict]:
        """Load download list from disk."""
        if os.path.exists(self.downloads_file):
            try:
                with open(self.downloads_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return []
