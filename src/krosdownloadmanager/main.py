"""KrosDownloadManager - Entry point."""

import logging
import os
import sys


def setup_logging() -> None:
    """Configure logging."""
    log_dir = os.path.join(os.path.expanduser("~"), ".krosdownloadmanager", "logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "krosdownloadmanager.log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    """Launch KrosDownloadManager."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting KrosDownloadManager v1.0")

    try:
        from krosdownloadmanager.gui.main_window import MainWindow

        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        raise


if __name__ == "__main__":
    main()
