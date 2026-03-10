"""Export benchmark results to CSV via pandas."""
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult

logger = get_logger(__name__)


def _result_to_row(r: BenchmarkResult) -> dict:
    return {
        "run_id": r.run_id,
        "timestamp": r.timestamp,
        "workload": r.workload_type,
        "model": r.model_name,
        "backend": r.backend,
        "device": r.device,
        "iterations": r.iterations,
        "batch_size": r.batch_size,
        "mean_latency_ms": r.latency.avg_ms if r.latency else None,
        "p50_latency_ms": r.latency.avg_ms if r.latency else None,
        "p95_latency_ms": r.latency.p95_ms if r.latency else None,
        "min_latency_ms": r.latency.min_ms if r.latency else None,
        "max_latency_ms": r.latency.max_ms if r.latency else None,
        "throughput_fps": r.throughput_fps,
        "cpu_mean_pct": r.resource_usage.avg_cpu_percent if r.resource_usage else None,
        "memory_peak_mb": r.resource_usage.max_memory_mb if r.resource_usage else None,
    }


def export_results_csv(results: List[BenchmarkResult], path: Path) -> Path:
    """Write results as a CSV table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [_result_to_row(r) for r in results]
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    logger.info("Exported CSV → %s", path)
    return path
