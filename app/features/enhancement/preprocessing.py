"""Image preprocessing for enhancement (super-resolution) models."""
from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path
from typing import Tuple


def preprocess_image(
    image_path: str | Path,
    target_size: Tuple[int, int] = (224, 224),
) -> np.ndarray:
    """Load and preprocess a low-res image for super-resolution. Returns NCHW float32 [0,1]."""
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    img = cv2.resize(img, target_size)
    img = img.astype(np.float32) / 255.0

    # Add batch and channel dims -> NCHW (1, 1, H, W) for grayscale
    img = np.expand_dims(img, axis=(0, 1))
    return img


def create_synthetic_input(
    target_size: Tuple[int, int] = (224, 224),
    batch_size: int = 1,
) -> np.ndarray:
    """Create a synthetic grayscale input tensor."""
    return np.random.rand(batch_size, 1, *target_size).astype(np.float32)
