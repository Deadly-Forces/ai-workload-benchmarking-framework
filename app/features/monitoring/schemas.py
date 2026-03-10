"""Monitoring schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MonitorSample:
    """A single monitoring sample."""
    timestamp: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    gpu_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    temperature_c: Optional[float] = None


@dataclass
class MonitoringData:
    """Collected monitoring data from a benchmark run."""
    samples: List[MonitorSample] = field(default_factory=list)
    sample_interval: float = 0.5
    duration_seconds: float = 0.0
