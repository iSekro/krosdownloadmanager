"""Utility helper functions."""

import re
from urllib.parse import urlparse


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    if size_bytes <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.2f} {units[unit_index]}"


def format_speed(bytes_per_sec: float) -> str:
    """Format download speed."""
    if bytes_per_sec <= 0:
        return "0 B/s"
    return f"{format_size(int(bytes_per_sec))}/s"


def is_valid_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https", "ftp"), result.netloc])
    except Exception:
        return False


def parse_url_from_clipboard(text: str) -> str:
    """Extract URL from clipboard text."""
    text = text.strip()
    if is_valid_url(text):
        return text

    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)

    return ""


def get_category_for_extension(ext: str, categories: dict) -> str:
    """Determine file category based on extension."""
    ext = ext.lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "General"


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, "_", filename)
    sanitized = sanitized.strip(". ")
    if not sanitized:
        sanitized = "download"
    return sanitized
