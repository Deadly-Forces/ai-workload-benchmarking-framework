"""Benchmark runner schemas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""

    workload_type: str = ""
    model_key: str = ""
    backend: str = "openvino"
    device: str = "CPU"
    iterations: int = 20
    warmup_iterations: int = 5
    batch_size: int = 1
    duration_seconds: Optional[float] = None  # For stress tests
    stress_target: str = ""  # cpu, gpu, memory, network, disk, cpu_gpu, all
    notes: str = ""
    num_threads: Optional[int] = None
    use_async: bool = False
    precision: str = "FP16"


@dataclass
class RunProgress:
    """Live progress information for a benchmark run."""

    phase: str = "idle"  # idle, warmup, running, analysis, complete, error
    current_iteration: int = 0
    total_iterations: int = 0
    elapsed_seconds: float = 0.0
    last_latency_ms: float = 0.0
    message: str = ""

    @property
    def progress_pct(self) -> float:
        if self.total_iterations <= 0:
            return 0.0
        return min(100.0, (self.current_iteration / self.total_iterations) * 100)
