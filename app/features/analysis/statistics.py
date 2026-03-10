"""Statistics helpers — derived metrics from raw latency data."""
from __future__ import annotations

from typing import List

import numpy as np


def coefficient_of_variation(values: List[float]) -> float:
    """CV = std / mean.  Returns 0 if list is empty."""
    if not values:
        return 0.0
    m = np.mean(values)
    return float(np.std(values) / m) if m != 0 else 0.0


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(values, p))


def interquartile_range(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(np.percentile(values, 75) - np.percentile(values, 25))


def outlier_count(values: List[float], factor: float = 1.5) -> int:
    """Count values beyond 1.5 * IQR from Q1/Q3."""
    if len(values) < 4:
        return 0
    q1, q3 = np.percentile(values, 25), np.percentile(values, 75)
    iqr = q3 - q1
    lo, hi = q1 - factor * iqr, q3 + factor * iqr
    return int(sum(1 for v in values if v < lo or v > hi))
