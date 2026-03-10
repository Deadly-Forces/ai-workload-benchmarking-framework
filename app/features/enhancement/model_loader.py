"""Enhancement model loader."""
from __future__ import annotations

from typing import Any

from app.config.constants import BACKEND_OPENVINO, BACKEND_ONNX, ENHANCEMENT_MODELS
from app.config.logging_config import get_logger
from app.core.exceptions import ModelLoadError
from app.core.paths import model_path

logger = get_logger(__name__)


class EnhancementModelLoader:
    """Handles loading super-resolution models."""

    def __init__(self, model_key: str, backend: str, device: str = "CPU"):
        self.model_key = model_key
        self.backend = backend
        self.device = device

        if model_key not in ENHANCEMENT_MODELS:
            raise ModelLoadError(f"Unknown enhancement model: {model_key}")
        self.model_config = ENHANCEMENT_MODELS[model_key]

    def load(self) -> Any:
        if self.backend == BACKEND_ONNX:
            return self._load_onnx()
        elif self.backend == BACKEND_OPENVINO:
            return self._load_openvino()
        else:
            raise ModelLoadError(f"Unsupported backend: {self.backend}")

    def _load_onnx(self) -> Any:
        try:
            import onnxruntime as ort
        except ImportError:
            raise ModelLoadError("ONNX Runtime is not installed")

        model_file = model_path(self.model_config["onnx_model"])
        if not model_file.exists():
            raise ModelLoadError(f"Model file not found: {model_file}")

        providers = ["CPUExecutionProvider"]
        if self.device == "GPU":
            providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
        session = ort.InferenceSession(str(model_file), providers=providers)
        logger.info("ONNX enhancement model loaded: %s", model_file.name)
        return session

    def _load_openvino(self) -> Any:
        try:
            from openvino import Core  # type: ignore[import-not-found]
        except ImportError:
            raise ModelLoadError("OpenVINO is not installed")

        model_file = model_path(self.model_config["onnx_model"])
        if not model_file.exists():
            raise ModelLoadError(f"Model file not found: {model_file}")

        core = Core()
        model = core.read_model(str(model_file))
        compiled = core.compile_model(model, self.device)
        logger.info("OpenVINO enhancement model loaded on %s", self.device)
        return compiled

    @property
    def scale_factor(self) -> int:
        return self.model_config.get("scale", 2)
