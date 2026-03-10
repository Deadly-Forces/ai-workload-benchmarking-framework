"""Consistency checker — compares repeated inference outputs for drift."""
from __future__ import annotations

import hashlib
from typing import List

import numpy as np

from app.config.constants import CONSISTENCY_TOLERANCE
from app.config.logging_config import get_logger
from app.features.reliability.schemas import ConsistencyRun, ReliabilityResult

logger = get_logger(__name__)


def _hash_array(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()


def check_consistency(
    outputs: List[np.ndarray],
    tolerance: float = CONSISTENCY_TOLERANCE,
) -> ReliabilityResult:
    """Compare a list of inference outputs against the first as reference."""
    if not outputs:
        return ReliabilityResult()

    reference = outputs[0]
    ref_hash = _hash_array(reference)
    runs: list[ConsistencyRun] = []
    drifts: list[float] = []

    for i, out in enumerate(outputs):
        h = _hash_array(out)
        diff = float(np.max(np.abs(out.astype(np.float64) - reference.astype(np.float64))))
        matches = diff <= tolerance
        runs.append(ConsistencyRun(
            iteration=i, output_hash=h,
            max_abs_diff=diff, matches_reference=matches,
        ))
        if not matches:
            drifts.append(diff)

    identical = sum(1 for r in runs if r.matches_reference)
    return ReliabilityResult(
        total_runs=len(outputs),
        identical_count=identical,
        drift_count=len(drifts),
        max_drift=max(drifts) if drifts else 0.0,
        mean_drift=float(np.mean(drifts)) if drifts else 0.0,
        tolerance_used=tolerance,
        all_consistent=(len(drifts) == 0),
        runs=runs,
    )
