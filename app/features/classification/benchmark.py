"""Classification benchmark — end-to-end image classification benchmarking."""
from __future__ import annotations

from typing import Any, Callable, Optional

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.config.constants import WORKLOAD_CLASSIFICATION
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.features.benchmark_runner.orchestrator import BenchmarkOrchestrator
from app.features.classification.model_loader import ClassificationModelLoader
from app.features.classification.preprocessing import create_synthetic_input, preprocess_image
from app.features.classification.inference import run_inference

logger = get_logger(__name__)


class ClassificationBenchmark:
    """Runs the image classification benchmark end-to-end."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.config.workload_type = WORKLOAD_CLASSIFICATION
        self._loader: Optional[ClassificationModelLoader] = None
        self._model: Any = None
        self._input_tensor: Any = None

    def run(
        self,
        progress_callback: Optional[Callable] = None,
        image_path: Optional[str] = None,
    ) -> BenchmarkResult:
        """Execute the classification benchmark."""
        self._loader = ClassificationModelLoader(
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
            input_size = loader.input_size
            if image_path:
                self._input_tensor = preprocess_image(image_path, target_size=input_size)
            else:
                self._input_tensor = create_synthetic_input(
                    target_size=input_size,
                    batch_size=self.config.batch_size,
                )
            return self._input_tensor

        def inference_fn(model, input_data):
            return run_inference(model, input_data, self.config.backend)

        result = orchestrator.run_standard_benchmark(load_fn, prepare_fn, inference_fn)
        return result
