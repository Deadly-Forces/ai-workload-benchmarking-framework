"""Run a sample classification benchmark from the CLI.

Usage:
    python scripts/run_sample_benchmark.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.constants import (
    WORKLOAD_CLASSIFICATION, BACKEND_OPENVINO, BACKEND_ONNX, DEVICE_CPU,
)
from app.config.logging_config import setup_logging, get_logger
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.features.classification.benchmark import ClassificationBenchmark
from app.features.reporting.export_json import export_result_json
from app.config.settings import EXPORTS_DIR

setup_logging()
logger = get_logger(__name__)


def main() -> None:
    config = BenchmarkConfig(
        workload_type=WORKLOAD_CLASSIFICATION,
        model_key="mobilenet-v2",
        backend=BACKEND_OPENVINO,
        device=DEVICE_CPU,
        iterations=20,
        warmup_iterations=5,
        batch_size=1,
    )

    logger.info("Starting sample benchmark: %s", config.model_key)

    bench = ClassificationBenchmark(config)

    def on_progress(p):
        logger.info("[%s] %s", p.phase, p.message)

    try:
        result = bench.run(progress_callback=on_progress)
    except Exception as e:
        logger.error("Benchmark failed: %s", e)
        # Try CPU-only fallback with ONNX
        config.backend = BACKEND_ONNX
        logger.info("Retrying with ONNX Runtime on CPU...")
        bench = ClassificationBenchmark(config)
        result = bench.run(progress_callback=on_progress)

    logger.info("Mean latency: %.2f ms", result.latency.avg_ms)
    logger.info("Throughput: %.1f FPS", result.throughput_fps)

    out = EXPORTS_DIR / f"sample_{result.run_id}.json"
    export_result_json(result, out)
    logger.info("Result saved → %s", out)


if __name__ == "__main__":
    main()
