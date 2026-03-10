"""High-resolution timer context manager."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class TimerResult:
    """Stores timing result."""
    elapsed_seconds: float = 0.0
    label: str = ""


class PrecisionTimer:
    """Context manager for precision timing."""

    def __init__(self, label: str = ""):
        self.label = label
        self._start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "PrecisionTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self.elapsed = time.perf_counter() - self._start

    @property
    def result(self) -> TimerResult:
        return TimerResult(elapsed_seconds=self.elapsed, label=self.label)

    @property
    def ms(self) -> float:
        return self.elapsed * 1000.0


@dataclass
class LatencyCollector:
    """Collects latency measurements from multiple runs."""
    latencies: List[float] = field(default_factory=list)

    def record(self, seconds: float) -> None:
        """Record a latency measurement in seconds."""
        self.latencies.append(seconds)

    def record_ms(self, milliseconds: float) -> None:
        """Record a latency measurement in milliseconds."""
        self.latencies.append(milliseconds / 1000.0)

    @property
    def count(self) -> int:
        return len(self.latencies)

    def clear(self) -> None:
        self.latencies.clear()
