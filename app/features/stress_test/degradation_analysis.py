"""Degradation analysis for stress tests."""
from __future__ import annotations

import numpy as np
from typing import List


def analyze_degradation(latencies_ms: List[float]) -> dict:
    """Analyze performance degradation over time.

    Compares first quarter average to last quarter average.
    """
    if len(latencies_ms) < 8:
        return {"degradation_detected": False, "drift_ms": 0.0, "drift_pct": 0.0}

    arr = np.array(latencies_ms)
    quarter = len(arr) // 4
    first_q = np.mean(arr[:quarter])
    last_q = np.mean(arr[-quarter:])
    drift = float(last_q - first_q)
    drift_pct = (drift / first_q * 100) if first_q > 0 else 0.0

    return {
        "degradation_detected": drift_pct > 10.0,  # >10% increase = degradation
        "drift_ms": round(drift, 3),
        "drift_pct": round(drift_pct, 2),
        "first_quarter_avg_ms": round(float(first_q), 3),
        "last_quarter_avg_ms": round(float(last_q), 3),
    }
