"""AI-powered auto-tuning for benchmarking configurations."""

from __future__ import annotations

from typing import Dict, Any, Optional

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.config.constants import (
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_STRESS,
    WORKLOAD_GENAI,
)
from app.features.classification.benchmark import ClassificationBenchmark
from app.features.detection.benchmark import DetectionBenchmark
from app.features.enhancement.benchmark import EnhancementBenchmark
from app.features.genai.benchmark import GenAIBenchmark
from app.features.stress_test.benchmark import StressTestBenchmark

logger = get_logger(__name__)

_RUNNERS = {
    WORKLOAD_CLASSIFICATION: ClassificationBenchmark,
    WORKLOAD_DETECTION: DetectionBenchmark,
    WORKLOAD_ENHANCEMENT: EnhancementBenchmark,
    WORKLOAD_GENAI: GenAIBenchmark,
    WORKLOAD_STRESS: StressTestBenchmark,
}


def evaluate_config(config: BenchmarkConfig) -> Optional[BenchmarkResult]:
    """Helper to run a short version of a benchmark and return the result."""
    runner_cls = _RUNNERS.get(config.workload_type)
    if not runner_cls:
        return None

    # We only need a short run to assess performance
    test_config = BenchmarkConfig(
        workload_type=config.workload_type,
        model_key=config.model_key,
        backend=config.backend,
        device=config.device,
        iterations=3,  # Keep it extremely short
        warmup_iterations=1,
        batch_size=config.batch_size,
        num_threads=config.num_threads,
        use_async=config.use_async,
        precision=config.precision,
    )

    try:
        runner = runner_cls(test_config)
        result = runner.run()
        if result.errors:
            logger.warning("Evaluation had errors: %s", result.errors)
            return None
        return result
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Evaluation failed for config: %s - Error: %s", test_config, e)
        return None


def optimize_batch_size(
    base_config: BenchmarkConfig, max_batch: int = 32
) -> Dict[str, Any]:
    """Find the optimal batch size via binary search/linear hybrid before OOM occurs.

    Returns a dict with the optimal config, history, and best throughput.
    """
    logger.info("Starting batch size optimization for %s", base_config.model_key)

    best_throughput = 0.0
    optimal_batch = base_config.batch_size
    history = []

    # Try successive batch sizes: 1, 2, 4, 8, 16, 32
    current_batch = 1

    while current_batch <= max_batch:
        logger.info("Evaluating batch size: %d", current_batch)
        config = BenchmarkConfig(
            **{**base_config.__dict__, "batch_size": current_batch}
        )

        try:
            result = evaluate_config(config)

            if not result:
                logger.warning(
                    "Failed to get result for batch %d, stopping search.", current_batch
                )
                break

            fps = result.throughput_fps
            history.append(
                {
                    "batch": current_batch,
                    "fps": fps,
                    "ram": result.resource_usage.max_memory_mb,
                }
            )

            # If throughput goes down, we've likely hit a memory/cache bottleneck or thermal limit
            if fps > best_throughput:
                best_throughput = fps
                optimal_batch = current_batch
            else:
                logger.info(
                    "Throughput dropped at batch size %d (%f vs best %f). Stopping.",
                    current_batch,
                    fps,
                    best_throughput,
                )
                break

            current_batch *= 2

        except Exception as e:  # pylint: disable=broad-except
            # Memory error or crash
            logger.info(
                "Exception during batch %d: %s. Treating as upper limit.",
                current_batch,
                e,
            )
            break

    return {
        "optimal_batch_size": optimal_batch,
        "best_throughput": best_throughput,
        "history": history,
    }


def find_optimal_thread_count(
    base_config: BenchmarkConfig, max_threads: int = 16
) -> Dict[str, Any]:
    """Find the optimal thread count for OpenVINO execution."""
    logger.info("Starting thread count optimization for %s", base_config.model_key)

    best_throughput = 0.0
    optimal_threads = base_config.num_threads or 4
    history = []

    # Test typical thread counts: 1, 2, 4, 6, 8, 12, 16
    thread_counts_to_test = [
        t for t in [1, 2, 4, 6, 8, 12, max_threads] if t <= max_threads
    ]

    for threads in thread_counts_to_test:
        logger.info("Evaluating thread count: %d", threads)
        config_args = base_config.__dict__.copy()
        config_args["num_threads"] = threads
        config = BenchmarkConfig(**config_args)

        try:
            result = evaluate_config(config)
            if not result:
                continue

            fps = result.throughput_fps
            history.append({"threads": threads, "fps": fps})

            if fps > best_throughput:
                best_throughput = fps
                optimal_threads = threads
            else:
                # Threads often have diminishing returns, but let's test all designated anchors
                pass

        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error evaluating thread count %d: %s", threads, e)
            break

    return {
        "optimal_num_threads": optimal_threads,
        "best_throughput": best_throughput,
        "history": history,
    }
