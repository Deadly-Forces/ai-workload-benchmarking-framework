"""Image preprocessing for detection models."""
from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path
from typing import Tuple


def preprocess_image(
    image_path: str | Path,
    target_size: Tuple[int, int] = (640, 640),
) -> np.ndarray:
    """Load and preprocess an image for detection inference.

    Returns NCHW float32 tensor normalized to [0, 1].
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    img = cv2.resize(img, target_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0

    # HWC -> NCHW
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img


def create_synthetic_input(
    target_size: Tuple[int, int] = (640, 640),
    batch_size: int = 1,
) -> np.ndarray:
    """Create a synthetic input tensor for benchmarking."""
    return np.random.rand(batch_size, 3, *target_size).astype(np.float32)
