"""Reliability runner — repeats inference and checks output consistency."""
from __future__ import annotations

from typing import Any, Callable, List, Optional

import numpy as np

from app.config.constants import WORKLOAD_CLASSIFICATION
from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.core.utils import generate_run_id, timestamp_now
from app.core.timer import PrecisionTimer
from app.features.benchmark_runner.schemas import BenchmarkConfig, RunProgress
from app.features.benchmark_runner.orchestrator import (
    compute_latency_stats, compute_resource_stats, compute_thermal_stats,
)
from app.features.monitoring.sampler import ResourceSampler
from app.features.reliability.consistency_checker import check_consistency
from app.features.reliability.schemas import ReliabilityResult

logger = get_logger(__name__)


class ReliabilityRunner:
    """Runs the same input through the model N times and checks consistency."""

    def __init__(
        self,
        config: BenchmarkConfig,
        load_fn: Callable,
        prepare_fn: Callable,
        inference_fn: Callable,
    ):
        self.config = config
        self.load_fn = load_fn
        self.prepare_fn = prepare_fn
        self.inference_fn = inference_fn
        self.progress = RunProgress()
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, cb: Callable) -> None:
        self._progress_callback = cb

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.progress, k):
                setattr(self.progress, k, v)
        if self._progress_callback:
            self._progress_callback(self.progress)

    def run(self) -> BenchmarkResult:
        run_id = generate_run_id()
        iterations = self.config.iterations
        errors: list[str] = []

        self._update(phase="loading", message="Loading model...")
        model = self.load_fn()
        input_data = self.prepare_fn()

        self._update(phase="running", message="Reliability test...")
        sampler = ResourceSampler()
        sampler.start()
        latencies: list[float] = []
        outputs: list[np.ndarray] = []

        for i in range(iterations):
            with PrecisionTimer() as t:
                try:
                    out = self.inference_fn(model, input_data)
                except Exception as e:
                    errors.append(str(e))
                    continue
            latencies.append(t.elapsed)
            if isinstance(out, np.ndarray):
                outputs.append(out.copy())
            self._update(
                current_iteration=i + 1,
                total_iterations=iterations,
                last_latency_ms=t.ms,
                message=f"Iteration {i+1}/{iterations}",
            )

        monitoring = sampler.stop()

        reliability: ReliabilityResult = check_consistency(outputs) if outputs else ReliabilityResult()

        latency_stats = compute_latency_stats(latencies)
        resource_stats = compute_resource_stats(monitoring)
        thermal_stats = compute_thermal_stats(monitoring)
        throughput = len(latencies) / sum(latencies) if latencies else 0.0

        self._update(phase="complete", message="Reliability test complete!")

        return BenchmarkResult(
            run_id=run_id, timestamp=timestamp_now(),
            workload_type="reliability",
            model_name=self.config.model_key,
            backend=self.config.backend, device=self.config.device,
            iterations=iterations, warmup_iterations=0,
            batch_size=self.config.batch_size,
            latency=latency_stats, throughput_fps=throughput,
            resource_usage=resource_stats, thermal=thermal_stats,
            notes=self.config.notes, errors=errors,
            extra={"reliability": reliability.__dict__},
        )
