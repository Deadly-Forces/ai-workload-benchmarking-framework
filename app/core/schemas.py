"""Core data schemas for benchmark results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LatencyStats:
    """Latency statistics for a benchmark run."""
    avg_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    p95_ms: float = 0.0
    std_ms: float = 0.0
    all_latencies_ms: List[float] = field(default_factory=list)


@dataclass
class ResourceStats:
    """Resource usage statistics."""
    avg_cpu_percent: float = 0.0
    max_cpu_percent: float = 0.0
    avg_memory_percent: float = 0.0
    max_memory_mb: float = 0.0
    samples: List[Dict[str, float]] = field(default_factory=list)


@dataclass
class ThermalStats:
    """Thermal statistics (optional)."""
    avg_temp_c: Optional[float] = None
    max_temp_c: Optional[float] = None
    available: bool = False
    samples: List[float] = field(default_factory=list)


@dataclass
class ConsistencyStats:
    """Output consistency statistics for reliability benchmarks."""
    score: float = 1.0
    max_deviation: float = 0.0
    mean_deviation: float = 0.0
    all_consistent: bool = True


@dataclass
class BenchmarkResult:
    """Complete result from a single benchmark run."""
    run_id: str = ""
    timestamp: str = ""
    workload_type: str = ""
    model_name: str = ""
    backend: str = ""
    device: str = ""
    iterations: int = 0
    warmup_iterations: int = 0
    batch_size: int = 1
    latency: LatencyStats = field(default_factory=LatencyStats)
    throughput_fps: float = 0.0
    resource_usage: ResourceStats = field(default_factory=ResourceStats)
    thermal: ThermalStats = field(default_factory=ThermalStats)
    consistency: Optional[ConsistencyStats] = None
    system_info: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    errors: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary."""
        from app.core.utils import safe_json_serialize
        return safe_json_serialize(self.__dict__)
