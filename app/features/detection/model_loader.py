"""Detection model loader."""
from __future__ import annotations

from typing import Any

from app.config.constants import BACKEND_OPENVINO, BACKEND_ONNX, DETECTION_MODELS
from app.config.logging_config import get_logger
from app.core.exceptions import ModelLoadError
from app.core.paths import model_path

logger = get_logger(__name__)


class DetectionModelLoader:
    """Handles loading detection models."""

    def __init__(self, model_key: str, backend: str, device: str = "CPU"):
        self.model_key = model_key
        self.backend = backend
        self.device = device

        if model_key not in DETECTION_MODELS:
            raise ModelLoadError(f"Unknown detection model: {model_key}")
        self.model_config = DETECTION_MODELS[model_key]

    def load(self) -> Any:
        """Load the model."""
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
        logger.info("ONNX detection model loaded: %s", model_file.name)
        return session

    def _load_openvino(self) -> Any:
        try:
            from openvino import Core  # type: ignore[import-not-found]
        except ImportError:
            raise ModelLoadError("OpenVINO is not installed")

        # Try to load ONNX model via OpenVINO
        model_file = model_path(self.model_config["onnx_model"])
        if not model_file.exists():
            raise ModelLoadError(f"Model file not found: {model_file}")

        core = Core()
        model = core.read_model(str(model_file))
        compiled = core.compile_model(model, self.device)
        logger.info("OpenVINO detection model loaded: %s on %s", model_file.name, self.device)
        return compiled

    @property
    def input_size(self):
        return self.model_config["input_size"]

    def load_labels(self) -> list[str]:
        labels_path = model_path(self.model_config.get("labels", ""))
        if labels_path.exists():
            return labels_path.read_text(encoding="utf-8").strip().split("\n")
        return []
