"""Aggregation helpers — summarise multiple benchmark results."""
from __future__ import annotations

from typing import List

import numpy as np

from app.core.schemas import BenchmarkResult
from app.features.analysis.schemas import AggregatedMetrics


def aggregate_results(results: List[BenchmarkResult]) -> AggregatedMetrics:
    """Compute aggregate metrics over a collection of runs."""
    if not results:
        return AggregatedMetrics()

    latencies = [r.latency.avg_ms for r in results if r.latency]
    throughputs = [r.throughput_fps for r in results]
    cpus = [r.resource_usage.avg_cpu_percent for r in results if r.resource_usage]
    mems = [r.resource_usage.max_memory_mb for r in results if r.resource_usage]

    return AggregatedMetrics(
        total_runs=len(results),
        mean_latency_ms=float(np.mean(latencies)) if latencies else 0.0,
        std_latency_ms=float(np.std(latencies)) if latencies else 0.0,
        mean_throughput_fps=float(np.mean(throughputs)) if throughputs else 0.0,
        best_throughput_fps=float(max(throughputs)) if throughputs else 0.0,
        worst_throughput_fps=float(min(throughputs)) if throughputs else 0.0,
        mean_cpu_pct=float(np.mean(cpus)) if cpus else 0.0,
        peak_memory_mb=float(max(mems)) if mems else 0.0,
    )
