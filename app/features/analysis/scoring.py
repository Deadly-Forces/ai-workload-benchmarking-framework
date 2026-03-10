"""Scoring — compute a weighted composite score for a benchmark result."""
from __future__ import annotations

from app.core.schemas import BenchmarkResult
from app.features.analysis.schemas import ScoreBreakdown
from app.features.analysis.statistics import coefficient_of_variation


def _normalise(value: float, lower: float, upper: float) -> float:
    """Map *value* to [0, 1] where lower=best and upper=worst."""
    if upper <= lower:
        return 1.0
    return max(0.0, min(1.0, 1.0 - (value - lower) / (upper - lower)))


def compute_score(
    result: BenchmarkResult,
    *,
    max_latency_ms: float = 200.0,
    max_throughput: float = 100.0,
    max_cpu_pct: float = 100.0,
) -> ScoreBreakdown:
    """Return a ScoreBreakdown for a single benchmark result."""
    sb = ScoreBreakdown()

    # Latency (lower is better)
    sb.latency_score = _normalise(
        result.latency.avg_ms if result.latency else max_latency_ms,
        0, max_latency_ms,
    ) * 100

    # Throughput (higher is better)
    tp = result.throughput_fps
    sb.throughput_score = min(tp / max_throughput, 1.0) * 100 if max_throughput else 0

    # Resource efficiency (lower CPU = better)
    cpu = result.resource_usage.avg_cpu_percent if result.resource_usage else max_cpu_pct
    sb.resource_score = _normalise(cpu, 0, max_cpu_pct) * 100

    # Stability (lower CV = better)
    all_lat = result.latency.all_latencies_ms if result.latency else []
    cv = coefficient_of_variation(all_lat)
    sb.stability_score = _normalise(cv, 0, 0.5) * 100

    w = sb.weights
    sb.overall = (
        w["latency"] * sb.latency_score
        + w["throughput"] * sb.throughput_score
        + w["resource"] * sb.resource_score
        + w["stability"] * sb.stability_score
    )
    return sb
