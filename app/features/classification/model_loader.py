"""Classification model loader for OpenVINO and ONNX Runtime."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from app.config.constants import BACKEND_OPENVINO, BACKEND_ONNX, CLASSIFICATION_MODELS
from app.config.logging_config import get_logger
from app.core.exceptions import ModelLoadError
from app.core.paths import model_path

logger = get_logger(__name__)


class ClassificationModelLoader:
    """Handles loading classification models for different backends."""

    def __init__(self, model_key: str, backend: str, device: str = "CPU"):
        self.model_key = model_key
        self.backend = backend
        self.device = device

        if model_key not in CLASSIFICATION_MODELS:
            raise ModelLoadError(f"Unknown classification model: {model_key}")
        self.model_config = CLASSIFICATION_MODELS[model_key]
        self._compiled_model: Any = None
        self._session: Any = None

    def load(self) -> Any:
        """Load the model using the configured backend."""
        if self.backend == BACKEND_OPENVINO:
            return self._load_openvino()
        elif self.backend == BACKEND_ONNX:
            return self._load_onnx()
        else:
            raise ModelLoadError(f"Unsupported backend: {self.backend}")

    def _load_openvino(self) -> Any:
        """Load model using OpenVINO (reads ONNX directly)."""
        try:
            from openvino import Core  # type: ignore[import-not-found]
        except ImportError:
            raise ModelLoadError("OpenVINO is not installed. Install with: pip install openvino")

        model_file = model_path(self.model_config["onnx_model"])
        if not model_file.exists():
            raise ModelLoadError(
                f"Model file not found: {model_file}\n"
                "Run 'python scripts/download_models.py' to download models."
            )

        logger.info("Loading OpenVINO model: %s on %s", model_file.name, self.device)
        core = Core()
        model = core.read_model(str(model_file))
        self._compiled_model = core.compile_model(model, self.device)
        logger.info("Model loaded successfully on %s", self.device)
        return self._compiled_model

    def _load_onnx(self) -> Any:
        """Load model using ONNX Runtime."""
        try:
            import onnxruntime as ort
        except ImportError:
            raise ModelLoadError("ONNX Runtime is not installed. Install with: pip install onnxruntime")

        model_file = model_path(self.model_config["onnx_model"])
        if not model_file.exists():
            raise ModelLoadError(
                f"Model file not found: {model_file}\n"
                "Run 'python scripts/download_models.py' to download models."
            )

        logger.info("Loading ONNX model: %s", model_file.name)
        providers = ["CPUExecutionProvider"]
        if self.device == "GPU":
            providers = ["DmlExecutionProvider", "CPUExecutionProvider"]

        self._session = ort.InferenceSession(str(model_file), providers=providers)
        logger.info("ONNX model loaded with providers: %s", self._session.get_providers())
        return self._session

    @property
    def input_size(self):
        return self.model_config["input_size"]

    def load_labels(self) -> list[str]:
        """Load class labels for the model."""
        labels_path = model_path(self.model_config.get("labels", ""))
        if labels_path.exists():
            return labels_path.read_text(encoding="utf-8").strip().split("\n")
        return []
