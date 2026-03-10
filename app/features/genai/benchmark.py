"""GenAI benchmark — LLM benchmarking with OpenVINO GenAI."""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.config.constants import WORKLOAD_GENAI
from app.config.settings import DEFAULT_MAX_NEW_TOKENS
from app.features.benchmark_runner.schemas import (
    BenchmarkConfig,
    RunProgress,
)
from app.features.benchmark_runner.orchestrator import BenchmarkOrchestrator
from app.features.genai.model_utils import GenAIModelLoader, get_default_prompt
from app.features.genai.schemas import GenMetrics

logger = get_logger(__name__)


class GenAIBenchmark:
    """Runs the GenAI LLM benchmark end-to-end and captures TTFT and TPS metrics."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.config.workload_type = WORKLOAD_GENAI
        self._loader: Optional[GenAIModelLoader] = None
        self._model: Any = None

        self._last_metrics: Optional[GenMetrics] = None

    def run(
        self,
        progress_callback: Optional[Callable] = None,
        prompt: Optional[str] = None,
    ) -> BenchmarkResult:
        """Execute the GenAI benchmark."""

        if prompt is None:
            prompt = get_default_prompt()

        def download_progress_hook(msg: str):
            if progress_callback:
                p = RunProgress(phase="Model Download", message=msg)
                progress_callback(p)

        self._loader = GenAIModelLoader(
            model_key=self.config.model_key,
            device=self.config.device,
            progress_callback=download_progress_hook,
        )

        orchestrator = BenchmarkOrchestrator(self.config)
        if progress_callback:
            orchestrator.set_progress_callback(progress_callback)

        def load_fn():
            self._model = self._loader.load()
            return self._model

        def prepare_fn():
            return prompt

        def inference_fn(model, input_data):
            try:
                import openvino_genai as ov_genai
            except ImportError as exc:
                raise ImportError(
                    "openvino-genai is not installed. Please install it to run GenAI workloads."
                ) from exc

            config = ov_genai.GenerationConfig()
            config.max_new_tokens = DEFAULT_MAX_NEW_TOKENS

            start_time = time.perf_counter()
            inference_fn.first_token_time = None

            def streamer(_subword: str) -> bool:
                """Callback function passed to generate() to catch the first token."""
                if getattr(inference_fn, "first_token_time", None) is None:
                    inference_fn.first_token_time = time.perf_counter()
                return False  # Return False to continue generation

            res = model.generate(input_data, config, streamer)
            end_time = time.perf_counter()

            ttft_ms = 0.0
            if inference_fn.first_token_time:
                ttft_ms = (inference_fn.first_token_time - start_time) * 1000.0
            else:
                ttft_ms = (end_time - start_time) * 1000.0

            try:
                tokenizer = model.get_tokenizer()
                encoded = tokenizer.encode(res)
                num_generated_tokens = len(encoded.input_ids)
            except Exception:  # pylint: disable=broad-except
                # Fallback approximation for token count if tokenizer encoding fails
                num_generated_tokens = len(res.split()) * 1.3

            gen_time_s = end_time - start_time
            tps = num_generated_tokens / gen_time_s if gen_time_s > 0 else 0

            self._last_metrics = GenMetrics(
                ttft_ms=ttft_ms,
                tps=tps,
                generated_text=res,
                generated_tokens=int(num_generated_tokens),
            )
            return res

        result = orchestrator.run_standard_benchmark(load_fn, prepare_fn, inference_fn)

        # Attach custom GenAI metrics
        if self._last_metrics:
            if not isinstance(result.extra, dict):
                result.extra = {}
            result.extra["gen_ttft_ms"] = self._last_metrics.ttft_ms
            result.extra["gen_tps"] = self._last_metrics.tps
            result.extra["gen_text"] = self._last_metrics.generated_text
            result.extra["gen_tokens"] = self._last_metrics.generated_tokens

            # Override throughput FPS to display Tokens Per Second automatically in the dashboard
            result.throughput_fps = self._last_metrics.tps

        return result
