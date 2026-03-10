"""Prepare sample datasets — create placeholder images for testing.

Usage:
    python scripts/prepare_datasets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.settings import DATASETS_DIR
from app.config.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def create_synthetic_images(count: int = 5, size: tuple = (640, 480)) -> None:
    """Generate synthetic PNG images for quick testing."""
    try:
        import cv2
    except ImportError:
        logger.error("OpenCV not installed — cannot generate images.")
        return

    out_dir = DATASETS_DIR / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        img = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
        path = out_dir / f"synthetic_{i:04d}.png"
        cv2.imwrite(str(path), img)
        logger.info("Created %s", path)

    logger.info("Generated %d synthetic images in %s", count, out_dir)


def main() -> None:
    create_synthetic_images()


if __name__ == "__main__":
    main()
