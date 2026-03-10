"""Schemas for the analysis / comparison feature."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ComparisonEntry:
    """One row in a side-by-side comparison table."""
    label: str = ""
    model_name: str = ""
    backend: str = ""
    device: str = ""
    mean_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    throughput_fps: float = 0.0
    cpu_mean_pct: float = 0.0
    memory_peak_mb: float = 0.0
    score: float = 0.0


@dataclass
class AggregatedMetrics:
    """Summary across multiple benchmark runs."""
    total_runs: int = 0
    mean_latency_ms: float = 0.0
    std_latency_ms: float = 0.0
    mean_throughput_fps: float = 0.0
    best_throughput_fps: float = 0.0
    worst_throughput_fps: float = 0.0
    mean_cpu_pct: float = 0.0
    peak_memory_mb: float = 0.0


@dataclass
class ScoreBreakdown:
    """Weighted scoring breakdown."""
    latency_score: float = 0.0
    throughput_score: float = 0.0
    resource_score: float = 0.0
    stability_score: float = 0.0
    overall: float = 0.0
    weights: Dict[str, float] = field(default_factory=lambda: {
        "latency": 0.30, "throughput": 0.30,
        "resource": 0.20, "stability": 0.20,
    })
