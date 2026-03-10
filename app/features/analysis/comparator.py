"""Comparator — build side-by-side comparison tables from results."""
from __future__ import annotations

from typing import List

from app.core.schemas import BenchmarkResult
from app.features.analysis.schemas import ComparisonEntry
from app.features.analysis.scoring import compute_score


def build_comparison(results: List[BenchmarkResult]) -> List[ComparisonEntry]:
    """Convert a list of BenchmarkResults into ComparisonEntry rows."""
    entries: list[ComparisonEntry] = []
    for r in results:
        score = compute_score(r)
        entries.append(ComparisonEntry(
            label=f"{r.model_name} / {r.backend} / {r.device}",
            model_name=r.model_name,
            backend=r.backend,
            device=r.device,
            mean_latency_ms=r.latency.avg_ms if r.latency else 0.0,
            p95_latency_ms=r.latency.p95_ms if r.latency else 0.0,
            throughput_fps=r.throughput_fps,
            cpu_mean_pct=r.resource_usage.avg_cpu_percent if r.resource_usage else 0.0,
            memory_peak_mb=r.resource_usage.max_memory_mb if r.resource_usage else 0.0,
            score=score.overall,
        ))
    entries.sort(key=lambda e: e.score, reverse=True)
    return entries
