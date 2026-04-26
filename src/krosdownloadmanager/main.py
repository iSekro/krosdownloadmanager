"""KrosDownloadManager - Entry point."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    """Configure logging with rotation (5 MB max, 3 backups)."""
    log_dir = os.path.join(os.path.expanduser("~"), ".krosdownloadmanager", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "krosdownloadmanager.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[file_handler, console_handler],
    )


def main() -> None:
    """Launch KrosDownloadManager."""
    setup_logging()
    logger = logging.getLogger(__name__)

    from krosdownloadmanager import __version__
    logger.info("Starting KrosDownloadManager v%s", __version__)

    try:
        from krosdownloadmanager.gui.main_window import MainWindow

        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        raise


if __name__ == "__main__":
    main()
