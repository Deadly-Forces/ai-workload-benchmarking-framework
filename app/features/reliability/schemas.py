"""Schemas for the reliability / consistency checker."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ConsistencyRun:
    """Stores per-iteration consistency information."""
    iteration: int = 0
    output_hash: str = ""
    max_abs_diff: float = 0.0
    matches_reference: bool = True


@dataclass
class ReliabilityResult:
    """Aggregate result of a consistency / reliability test."""
    total_runs: int = 0
    identical_count: int = 0
    drift_count: int = 0
    max_drift: float = 0.0
    mean_drift: float = 0.0
    tolerance_used: float = 1e-5
    all_consistent: bool = True
    runs: List[ConsistencyRun] = field(default_factory=list)
