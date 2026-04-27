# Testing KrosDownloadManager

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev,build]"

# Run unit tests
pytest tests/ -v

# Lint
ruff check src/

# Launch app (Linux with X11)
DISPLAY=:0 python -m krosdownloadmanager
```

## API Server

The app starts an HTTP API server on `localhost:29256` for browser extension communication. This is also useful for automated testing.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | App status, version, active/total download counts |
| POST | `/download` | Add a single download: `{"url": "..."}` |
| POST | `/download_batch` | Add multiple: `{"urls": ["url1", "url2"]}` |
| POST | `/file_info` | Get file metadata: `{"url": "..."}` |

### Example

```bash
# Check if app is running
curl http://localhost:29256/status

# Add a download via API
curl -X POST http://localhost:29256/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/bytes/10240"}'
```

## GUI Testing on Linux

### Known Limitation: Frameless Window

The app uses a **frameless CustomTkinter window** (no native title bar). On Linux, automated mouse clicks (computer tool, xdotool) may not register on this window type. Buttons, keyboard shortcuts, and right-click menus might not be triggerable via automation.

**Workaround:** Use the API to add downloads and verify visual state via screenshots. The API `/download` endpoint triggers the same code path as the GUI "New Download" dialog.

### Features That Require Manual Testing on Windows

- Search bar filtering (typing in the search field)
- Double-click behavior (pause/resume/open file)
- Context menu options (right-click on download row)
- Drag & drop URLs
- Keyboard shortcuts (Ctrl+N, Ctrl+B, Ctrl+T, etc.)

## Useful Test URLs

| URL | Size | Purpose |
|-----|------|---------|
| `https://httpbin.org/bytes/10240` | 10 KB | Quick completion test |
| `https://proof.ovh.net/files/100Mb.dat` | 100 MB | Medium download, tests progress display |
| `https://proof.ovh.net/files/1Gb.dat` | 1 GB | Long download, tests titlebar speed indicator |

**Avoid:** GitHub raw URLs may 404 depending on branch. Use httpbin.org or proof.ovh.net for reliable test files.

## Key File Locations

- **Config:** `~/.krosdownloadmanager/config.json`
- **Logs:** `~/.krosdownloadmanager/logs/krosdownloadmanager.log` (rotating, 5MB max, 3 backups)
- **Downloads:** `~/Downloads/KrosDownloads/` (default)
- **Saved downloads state:** `~/.krosdownloadmanager/downloads.json`

## Known Issues to Watch For

- **Race condition on fast downloads:** Downloads completing in < 1s may show stale values in the GUI row ("0 B", "Descargando") because the download finishes before the row widget is created. The status bar and engine track the correct state. This affects small files only.
- **Segoe UI Emoji font on Linux:** Never use "Segoe UI Emoji" font in CustomTkinter on Linux — it causes segfaults. Always use the `FONT_FAMILY` variable instead.
- **Toast timing:** Toast notifications auto-dismiss after 3 seconds. Screenshot immediately after download completion to capture them.

## Devin Secrets Needed

No secrets required for local testing. The app runs entirely locally with no external authentication.
