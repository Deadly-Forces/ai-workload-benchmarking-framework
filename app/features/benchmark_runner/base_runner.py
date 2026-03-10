"""Abstract base for benchmark runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.schemas import BenchmarkResult
from app.features.benchmark_runner.schemas import BenchmarkConfig, RunProgress


class BaseBenchmarkRunner(ABC):
    """Abstract base class for workload-specific benchmark runners."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.progress = RunProgress()
        self._model: Any = None

    @abstractmethod
    def load_model(self) -> None:
        """Load the model for inference."""

    @abstractmethod
    def prepare_input(self) -> Any:
        """Prepare input data for inference."""

    @abstractmethod
    def run_inference(self, input_data: Any) -> Any:
        """Execute a single inference."""

    @abstractmethod
    def run(self) -> BenchmarkResult:
        """Execute the full benchmark and return results."""

    def cleanup(self) -> None:
        """Clean up resources. Override if needed."""
        self._model = None

    def update_progress(
        self,
        phase: str = "",
        iteration: int = 0,
        total: int = 0,
        elapsed: float = 0.0,
        latency: float = 0.0,
        message: str = "",
    ) -> None:
        """Update current progress state."""
        if phase:
            self.progress.phase = phase
        if iteration:
            self.progress.current_iteration = iteration
        if total:
            self.progress.total_iterations = total
        if elapsed:
            self.progress.elapsed_seconds = elapsed
        if latency:
            self.progress.last_latency_ms = latency
        if message:
            self.progress.message = message
