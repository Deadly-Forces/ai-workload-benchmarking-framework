"""Image quality metrics for enhancement benchmarks."""
from __future__ import annotations

import numpy as np
from typing import Optional


def compute_psnr(original: np.ndarray, enhanced: np.ndarray, max_val: float = 1.0) -> float:
    """Compute Peak Signal-to-Noise Ratio."""
    mse = np.mean((original.astype(np.float64) - enhanced.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return float(10.0 * np.log10((max_val ** 2) / mse))


def compute_ssim_simple(
    original: np.ndarray,
    enhanced: np.ndarray,
    max_val: float = 1.0,
) -> float:
    """Compute a simplified SSIM score."""
    c1 = (0.01 * max_val) ** 2
    c2 = (0.03 * max_val) ** 2

    mu_x = np.mean(original)
    mu_y = np.mean(enhanced)
    sigma_x = np.std(original)
    sigma_y = np.std(enhanced)
    sigma_xy = np.mean((original - mu_x) * (enhanced - mu_y))

    numerator = (2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)
    denominator = (mu_x ** 2 + mu_y ** 2 + c1) * (sigma_x ** 2 + sigma_y ** 2 + c2)

    return float(numerator / denominator)
