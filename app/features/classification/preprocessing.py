"""Image preprocessing for classification models."""
from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path
from typing import Tuple


def preprocess_image(
    image_path: str | Path,
    target_size: Tuple[int, int] = (224, 224),
    normalize: bool = True,
) -> np.ndarray:
    """Load and preprocess an image for classification inference.

    Returns NCHW float32 tensor.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    img = cv2.resize(img, target_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)

    if normalize:
        # ImageNet normalization
        mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
        std = np.array([58.395, 57.12, 57.375], dtype=np.float32)
        img = (img - mean) / std

    # HWC -> NCHW
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img


def create_synthetic_input(
    target_size: Tuple[int, int] = (224, 224),
    batch_size: int = 1,
) -> np.ndarray:
    """Create a synthetic input tensor for benchmarking."""
    return np.random.randn(batch_size, 3, *target_size).astype(np.float32)
