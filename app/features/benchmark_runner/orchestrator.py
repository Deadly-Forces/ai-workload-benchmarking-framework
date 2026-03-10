"""Benchmark orchestrator — coordinates benchmark execution."""

from __future__ import annotations

from typing import Optional, Callable
import numpy as np

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult, LatencyStats, ResourceStats, ThermalStats
from app.core.utils import generate_run_id, timestamp_now
from app.core.timer import PrecisionTimer, LatencyCollector
from app.features.benchmark_runner.schemas import BenchmarkConfig, RunProgress
from app.features.benchmark_runner.warmup import run_warmup
from app.features.monitoring.sampler import ResourceSampler
from app.features.monitoring.anomaly_detector import AnomalyDetector
from app.features.system_profile.profiler import build_system_profile

logger = get_logger(__name__)


def compute_latency_stats(latencies_s: list[float]) -> LatencyStats:
    """Compute latency statistics from a list of measurements in seconds."""
    if not latencies_s:
        return LatencyStats()
    arr = np.array(latencies_s) * 1000.0  # Convert to ms
    return LatencyStats(
        avg_ms=float(np.mean(arr)),
        min_ms=float(np.min(arr)),
        max_ms=float(np.max(arr)),
        p95_ms=float(np.percentile(arr, 95)),
        std_ms=float(np.std(arr)),
        all_latencies_ms=arr.tolist(),
    )


def compute_resource_stats(monitoring_data) -> ResourceStats:
    """Compute resource statistics from monitoring data."""
    if not monitoring_data or not monitoring_data.samples:
        return ResourceStats()
    samples = monitoring_data.samples
    cpu_vals = [s.cpu_percent for s in samples]
    mem_vals = [s.memory_percent for s in samples]
    mem_mb_vals = [s.memory_mb for s in samples]
    return ResourceStats(
        avg_cpu_percent=float(np.mean(cpu_vals)) if cpu_vals else 0,
        max_cpu_percent=float(np.max(cpu_vals)) if cpu_vals else 0,
        avg_memory_percent=float(np.mean(mem_vals)) if mem_vals else 0,
        max_memory_mb=float(np.max(mem_mb_vals)) if mem_mb_vals else 0,
        samples=[
            {
                "ts": s.timestamp,
                "cpu": s.cpu_percent,
                "mem": s.memory_percent,
                "mem_mb": s.memory_mb,
            }
            for s in samples
        ],
    )


def compute_thermal_stats(monitoring_data) -> ThermalStats:
    """Compute thermal statistics from monitoring data."""
    if not monitoring_data or not monitoring_data.samples:
        return ThermalStats(available=False)
    temps = [
        s.temperature_c for s in monitoring_data.samples if s.temperature_c is not None
    ]
    if not temps:
        return ThermalStats(available=False)
    return ThermalStats(
        avg_temp_c=float(np.mean(temps)),
        max_temp_c=float(np.max(temps)),
        available=True,
        samples=temps,
    )


class BenchmarkOrchestrator:
    """Orchestrates benchmark execution with monitoring and analysis."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.progress = RunProgress()
        self._progress_callback: Optional[Callable[[RunProgress], None]] = None

    def set_progress_callback(self, callback: Callable[[RunProgress], None]) -> None:
        """Set a callback for progress updates."""
        self._progress_callback = callback

    def _update_progress(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        if self._progress_callback:
            self._progress_callback(self.progress)

    def run_standard_benchmark(
        self,
        load_fn: Callable,
        prepare_fn: Callable,
        inference_fn: Callable,
    ) -> BenchmarkResult:
        """Execute a standard benchmark (load, warmup, iterate, collect stats)."""
        run_id = generate_run_id()
        logger.info("Starting benchmark run: %s", run_id)
        errors = []

        # Phase 1: Load model
        self._update_progress(phase="loading", message="Loading model...")
        try:
            model = load_fn()
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Model loading failed: %s", e)
            return BenchmarkResult(
                run_id=run_id,
                timestamp=timestamp_now(),
                workload_type=self.config.workload_type,
                model_name=self.config.model_key,
                backend=self.config.backend,
                device=self.config.device,
                errors=[str(e)],
                notes="Model loading failed",
            )

        # Initialize Anomaly Detector
        self._update_progress(
            phase="preparing", message="Initializing anomaly detector..."
        )
        anomaly_detector = AnomalyDetector(contamination=0.05)

        # Phase 2: Prepare input
        self._update_progress(phase="preparing", message="Preparing input data...")
        try:
            input_data = prepare_fn()
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Input preparation failed: %s", e)
            return BenchmarkResult(
                run_id=run_id,
                timestamp=timestamp_now(),
                workload_type=self.config.workload_type,
                model_name=self.config.model_key,
                backend=self.config.backend,
                device=self.config.device,
                errors=[str(e)],
                notes="Input preparation failed",
            )

        # Phase 3: Warmup
        self._update_progress(phase="warmup", message="Warming up...")
        try:
            run_warmup(
                lambda: inference_fn(model, input_data), self.config.warmup_iterations
            )
        except Exception as e:  # pylint: disable=broad-except
            errors.append(f"Warmup issue: {e}")
            logger.warning("Warmup error: %s", e)

        # Train baseline with warmup samples if available
        # But wait, run_warmup doesn't collect samples.
        # Let's do a quick baseline run with the sampler.
        self._update_progress(phase="warmup", message="Training hardware baseline...")
        baseline_sampler = ResourceSampler()
        baseline_sampler.start()
        try:
            # Re-use warmup iterations count, but run inference directly
            for _ in range(max(3, self.config.warmup_iterations or 3)):
                inference_fn(model, input_data)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Baseline training inference error: %s", e)
        baseline_data = baseline_sampler.stop()
        if baseline_data and baseline_data.samples:
            anomaly_detector.train_baseline_profile(baseline_data.samples)

        # Phase 4: Benchmark iterations with monitoring
        self._update_progress(
            phase="running",
            message="Running benchmark...",
            total_iterations=self.config.iterations,
        )
        sampler = ResourceSampler()
        sampler.start()
        collector = LatencyCollector()

        with PrecisionTimer("total_benchmark") as total_timer:
            for i in range(self.config.iterations):
                with PrecisionTimer(f"iter_{i}") as iter_timer:
                    try:
                        inference_fn(model, input_data)
                    except Exception as e:  # pylint: disable=broad-except
                        errors.append(f"Iteration {i} error: {e}")
                        logger.warning("Inference error at iteration %d: %s", i, e)
                        continue
                collector.record(iter_timer.elapsed)
                self._update_progress(
                    current_iteration=i + 1,
                    # pylint: disable=protected-access
                    elapsed_seconds=total_timer._start
                    and (__import__("time").perf_counter() - total_timer._start),
                    # pylint: enable=protected-access
                    last_latency_ms=iter_timer.ms,
                    message=f"Iteration {i + 1}/{self.config.iterations}",
                )

                # Check for anomalies periodically (every 5 iterations or at the end)
                if anomaly_detector.is_trained and (
                    i % 5 == 0 or i == self.config.iterations - 1
                ):
                    recent_samples = sampler.get_current_samples()
                    if recent_samples:
                        anomaly_res = anomaly_detector.detect_system_anomalies(
                            recent_samples
                        )
                        if anomaly_res.get("has_anomaly"):
                            self._update_progress(
                                message=(
                                    f"Iteration {i + 1}/{self.config.iterations} "
                                    f"- {anomaly_res['message']}"
                                )
                            )
                            errors.append(anomaly_res["message"])

        monitoring_data = sampler.stop()

        # Phase 5: Compute statistics
        self._update_progress(phase="analysis", message="Computing statistics...")
        latency_stats = compute_latency_stats(collector.latencies)
        resource_stats = compute_resource_stats(monitoring_data)
        thermal_stats = compute_thermal_stats(monitoring_data)
        throughput = (
            (collector.count / total_timer.elapsed) if total_timer.elapsed > 0 else 0.0
        )

        # Build system info
        try:
            sys_profile = build_system_profile()
            sys_info = sys_profile.to_dict()
        except Exception:  # pylint: disable=broad-except
            sys_info = {}

        self._update_progress(phase="complete", message="Benchmark complete!")

        return BenchmarkResult(
            run_id=run_id,
            timestamp=timestamp_now(),
            workload_type=self.config.workload_type,
            model_name=self.config.model_key,
            backend=self.config.backend,
            device=self.config.device,
            iterations=collector.count,
            warmup_iterations=self.config.warmup_iterations,
            batch_size=self.config.batch_size,
            latency=latency_stats,
            throughput_fps=throughput,
            resource_usage=resource_stats,
            thermal=thermal_stats,
            system_info=sys_info,
            notes=self.config.notes,
            errors=errors,
        )
