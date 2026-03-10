"""Download pre-trained models from public ONNX model sources.

Usage:
    python scripts/download_models.py [--all | --classification | --detection | --enhancement]
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

# Ensure project root importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.settings import MODELS_DIR
from app.config.constants import CLASSIFICATION_MODELS, DETECTION_MODELS, ENHANCEMENT_MODELS
from app.config.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# ── Public ONNX model URLs ───────────────────────────────────────────
_DOWNLOAD_URLS = {
    "classification/mobilenet-v2.onnx": (
        "https://github.com/onnx/models/raw/main/validated/vision/"
        "classification/mobilenet/model/mobilenetv2-12.onnx"
    ),
    "detection/yolov8n.onnx": (
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx"
    ),
    "enhancement/espcn_x2.onnx": (
        "https://github.com/onnx/models/raw/main/validated/vision/"
        "super_resolution/sub_pixel_cnn_2016/model/super-resolution-10.onnx"
    ),
}


def _download_file(url: str, dest: Path) -> None:
    """Download a file from *url* to *dest* with progress logging."""
    if dest.exists():
        logger.info("Already exists: %s", dest)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s → %s", url.split("/")[-1], dest)
    urllib.request.urlretrieve(url, str(dest))  # noqa: S310
    logger.info("Saved %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)


def _export_yolov8n(dest: Path) -> None:
    """Export YOLOv8n to ONNX using the ultralytics package."""
    if dest.exists():
        logger.info("Already exists: %s", dest)
        return
    try:
        from ultralytics import YOLO  # type: ignore[import-untyped]
    except ImportError:
        logger.error(
            "ultralytics package not installed. "
            "Run: pip install ultralytics   then re-run this script."
        )
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Exporting YOLOv8n → ONNX (requires internet for .pt download)…")
    model = YOLO("yolov8n.pt")
    exported = model.export(format="onnx", imgsz=640)
    exported_path = Path(str(exported))
    exported_path.rename(dest)
    # Clean up .pt file left in cwd
    pt_file = Path("yolov8n.pt")
    if pt_file.exists():
        pt_file.unlink()
    logger.info("Saved %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)


# ── per-workload downloaders ──────────────────────────────────────────
def download_classification() -> None:
    for _key, info in CLASSIFICATION_MODELS.items():
        onnx_rel = info.get("onnx_model")
        if onnx_rel and onnx_rel in _DOWNLOAD_URLS:
            _download_file(_DOWNLOAD_URLS[onnx_rel], MODELS_DIR / onnx_rel)


def download_detection() -> None:
    for _key, info in DETECTION_MODELS.items():
        onnx_rel = info.get("onnx_model")
        if not onnx_rel:
            continue
        dest = MODELS_DIR / onnx_rel
        if "yolov8" in onnx_rel:
            _export_yolov8n(dest)
        elif onnx_rel in _DOWNLOAD_URLS:
            _download_file(_DOWNLOAD_URLS[onnx_rel], dest)


def download_enhancement() -> None:
    for _key, info in ENHANCEMENT_MODELS.items():
        onnx_rel = info.get("onnx_model")
        if onnx_rel and onnx_rel in _DOWNLOAD_URLS:
            _download_file(_DOWNLOAD_URLS[onnx_rel], MODELS_DIR / onnx_rel)


# ── CLI ───────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Download pre-trained models")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--classification", action="store_true")
    parser.add_argument("--detection", action="store_true")
    parser.add_argument("--enhancement", action="store_true")
    args = parser.parse_args()

    if args.all or (not args.classification and not args.detection and not args.enhancement):
        download_classification()
        download_detection()
        download_enhancement()
    else:
        if args.classification:
            download_classification()
        if args.detection:
            download_detection()
        if args.enhancement:
            download_enhancement()

    logger.info("Done. Models are in: %s", MODELS_DIR)


if __name__ == "__main__":
    main()
