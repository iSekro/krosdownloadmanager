"""Tests for utility helper functions."""

from krosdownloadmanager.utils.helpers import (
    extract_urls_from_text,
    format_eta,
    format_size,
    format_speed,
    get_category_for_extension,
    is_valid_url,
    parse_url_from_clipboard,
    sanitize_filename,
)


def test_format_size_zero():
    assert format_size(0) == "0 B"


def test_format_size_bytes():
    assert format_size(500) == "500 B"


def test_format_size_kb():
    result = format_size(1536)
    assert "KB" in result
    assert "1.50" in result


def test_format_size_mb():
    result = format_size(10 * 1024 * 1024)
    assert "MB" in result


def test_format_size_gb():
    result = format_size(2 * 1024 * 1024 * 1024)
    assert "GB" in result


def test_format_speed_zero():
    assert format_speed(0) == "0 B/s"


def test_format_speed_nonzero():
    result = format_speed(1024 * 1024)
    assert "/s" in result
    assert "MB" in result


def test_is_valid_url_valid():
    assert is_valid_url("https://example.com/file.zip")
    assert is_valid_url("http://example.com/path/file.exe")
    assert is_valid_url("https://cdn.example.com/downloads/v1.2.3/file.tar.gz")


def test_is_valid_url_invalid():
    assert not is_valid_url("")
    assert not is_valid_url("not a url")
    assert not is_valid_url("ftp://")
    assert not is_valid_url("just text")


def test_parse_url_from_clipboard_direct():
    assert parse_url_from_clipboard("https://example.com/file.zip") == "https://example.com/file.zip"


def test_parse_url_from_clipboard_with_text():
    text = "Download from https://example.com/file.zip here"
    assert parse_url_from_clipboard(text) == "https://example.com/file.zip"


def test_parse_url_from_clipboard_no_url():
    assert parse_url_from_clipboard("just some text") == ""


def test_sanitize_filename():
    assert sanitize_filename("normal_file.txt") == "normal_file.txt"
    assert sanitize_filename('file<>:"/\\|?*.txt') == "file_________.txt"
    assert sanitize_filename("") == "download"
    assert sanitize_filename("...") == "download"


def test_get_category_for_extension():
    categories = {
        "Video": [".mp4", ".mkv"],
        "Music": [".mp3", ".flac"],
        "General": [],
    }
    assert get_category_for_extension(".mp4", categories) == "Video"
    assert get_category_for_extension(".mp3", categories) == "Music"
    assert get_category_for_extension(".xyz", categories) == "General"


def test_format_eta_zero():
    assert format_eta(0) == "00:00"


def test_format_eta_seconds():
    assert format_eta(65) == "01:05"


def test_format_eta_hours():
    result = format_eta(7200)
    assert "h" in result


def test_format_eta_days():
    result = format_eta(100000)
    assert "d" in result


def test_extract_urls_from_text():
    text = "Download from https://example.com/file1.zip and https://example.com/file2.exe here"
    urls = extract_urls_from_text(text)
    assert len(urls) == 2
    assert "https://example.com/file1.zip" in urls
    assert "https://example.com/file2.exe" in urls


def test_extract_urls_from_text_empty():
    assert extract_urls_from_text("no urls here") == []


def test_extract_urls_from_text_multiline():
    text = """https://example.com/file1.zip
https://example.com/file2.zip
https://example.com/file3.zip"""
    urls = extract_urls_from_text(text)
    assert len(urls) == 3
