"""Stress test benchmark — adapter matching the standard benchmark interface."""
from __future__ import annotations

from typing import Any, Callable, Optional

from app.config.constants import WORKLOAD_STRESS
from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.features.classification.model_loader import ClassificationModelLoader
from app.features.classification.preprocessing import create_synthetic_input
from app.features.classification.inference import run_inference
from app.features.stress_test.runner import StressTestRunner

logger = get_logger(__name__)


class StressTestBenchmark:
    """Wraps StressTestRunner with the same interface as other benchmarks."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.config.workload_type = WORKLOAD_STRESS

    def run(
        self,
        progress_callback: Optional[Callable] = None,
    ) -> BenchmarkResult:
        loader = ClassificationModelLoader(
            model_key=self.config.model_key,
            backend=self.config.backend,
            device=self.config.device,
        )
        input_size = loader.input_size

        def load_fn():
            return loader.load()

        def prepare_fn():
            return create_synthetic_input(
                target_size=input_size,
                batch_size=self.config.batch_size,
            )

        def inference_fn(model, input_data):
            return run_inference(model, input_data, self.config.backend)

        runner = StressTestRunner(self.config, load_fn, prepare_fn, inference_fn)
        if progress_callback:
            runner.set_progress_callback(progress_callback)
        return runner.run()
