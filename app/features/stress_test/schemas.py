"""Stress test schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StressTestResult:
    """Additional stress test metrics."""
    total_duration_s: float = 0.0
    total_inferences: int = 0
    latency_drift_ms: float = 0.0  # difference between first and last quarter avg
    degradation_detected: bool = False
    latency_over_time_ms: List[float] = field(default_factory=list)
    cpu_over_time: List[float] = field(default_factory=list)
    memory_over_time: List[float] = field(default_factory=list)
    stress_target: str = "cpu"
