"""Detection benchmark."""
from __future__ import annotations

from typing import Any, Callable, Optional

from app.config.constants import WORKLOAD_DETECTION
from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.features.benchmark_runner.orchestrator import BenchmarkOrchestrator
from app.features.detection.model_loader import DetectionModelLoader
from app.features.detection.preprocessing import create_synthetic_input
from app.features.detection.inference import run_inference

logger = get_logger(__name__)


class DetectionBenchmark:
    """Runs the object detection benchmark."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.config.workload_type = WORKLOAD_DETECTION
        self._loader: Optional[DetectionModelLoader] = None
        self._model: Any = None

    def run(self, progress_callback: Optional[Callable] = None) -> BenchmarkResult:
        self._loader = DetectionModelLoader(
            model_key=self.config.model_key,
            backend=self.config.backend,
            device=self.config.device,
        )
        loader = self._loader

        orchestrator = BenchmarkOrchestrator(self.config)
        if progress_callback:
            orchestrator.set_progress_callback(progress_callback)

        def load_fn():
            self._model = loader.load()
            return self._model

        def prepare_fn():
            return create_synthetic_input(
                target_size=loader.input_size,
                batch_size=self.config.batch_size,
            )

        def inference_fn(model, input_data):
            return run_inference(model, input_data, self.config.backend)

        return orchestrator.run_standard_benchmark(load_fn, prepare_fn, inference_fn)
