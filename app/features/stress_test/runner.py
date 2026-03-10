"""Stress test runner — runs inference continuously for a configured duration."""
from __future__ import annotations

import time
from typing import Any, Callable, Optional

import numpy as np

from app.config.constants import WORKLOAD_STRESS
from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.core.utils import generate_run_id, timestamp_now
from app.core.timer import PrecisionTimer
from app.features.benchmark_runner.schemas import BenchmarkConfig, RunProgress
from app.features.benchmark_runner.orchestrator import (
    compute_latency_stats, compute_resource_stats, compute_thermal_stats,
)
from app.features.monitoring.sampler import ResourceSampler
from app.features.stress_test.schemas import StressTestResult
from app.features.stress_test.degradation_analysis import analyze_degradation
from app.features.stress_test.stress_generators import StressManager

logger = get_logger(__name__)


class StressTestRunner:
    """Runs a selected model continuously for a configurable duration."""

    def __init__(
        self,
        config: BenchmarkConfig,
        load_fn: Callable,
        prepare_fn: Callable,
        inference_fn: Callable,
    ):
        self.config = config
        self.config.workload_type = WORKLOAD_STRESS
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
        duration = self.config.duration_seconds or 60.0
        stress_target = self.config.stress_target or "cpu"
        errors = []

        # Load
        self._update(phase="loading", message="Loading model...")
        model = self.load_fn()
        input_data = self.prepare_fn()

        # Start component stress workers
        stress_mgr = StressManager(stress_target)
        self._update(phase="running", message=f"Stress test ({stress_target}) for {duration}s...")
        stress_mgr.start()

        sampler = ResourceSampler()
        sampler.start()
        latencies = []
        start = time.perf_counter()

        while (time.perf_counter() - start) < duration:
            with PrecisionTimer() as t:
                try:
                    self.inference_fn(model, input_data)
                except Exception as e:
                    errors.append(str(e))
                    continue
            latencies.append(t.elapsed)
            elapsed = time.perf_counter() - start
            self._update(
                current_iteration=len(latencies),
                elapsed_seconds=elapsed,
                last_latency_ms=t.ms,
                message=f"Elapsed {elapsed:.1f}s / {duration}s — {len(latencies)} inferences",
            )

        monitoring = sampler.stop()
        stress_mgr.stop()
        total_time = time.perf_counter() - start

        # Analysis
        latency_stats = compute_latency_stats(latencies)
        resource_stats = compute_resource_stats(monitoring)
        thermal_stats = compute_thermal_stats(monitoring)
        throughput = len(latencies) / total_time if total_time > 0 else 0.0
        degradation = analyze_degradation(latency_stats.all_latencies_ms)

        stress_data = StressTestResult(
            total_duration_s=total_time,
            total_inferences=len(latencies),
            latency_drift_ms=degradation["drift_ms"],
            degradation_detected=degradation["degradation_detected"],
            latency_over_time_ms=latency_stats.all_latencies_ms,
            stress_target=stress_target,
        )

        self._update(phase="complete", message="Stress test complete!")

        result = BenchmarkResult(
            run_id=run_id, timestamp=timestamp_now(),
            workload_type=WORKLOAD_STRESS,
            model_name=self.config.model_key,
            backend=self.config.backend, device=self.config.device,
            iterations=len(latencies), warmup_iterations=0,
            batch_size=self.config.batch_size,
            latency=latency_stats, throughput_fps=throughput,
            resource_usage=resource_stats, thermal=thermal_stats,
            notes=self.config.notes, errors=errors,
            extra={"stress_test": stress_data.__dict__, "degradation": degradation},
        )
        return result
