"""Utilities for loading OpenVINO GenAI models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional
from huggingface_hub import snapshot_download

from app.config.logging_config import get_logger
from app.config.constants import GENAI_MODELS
from app.config.settings import MODELS_DIR

logger = get_logger(__name__)


class GenAIModelLoader:
    """Loads OpenVINO Generative AI LLMPipeline models."""

    def __init__(
        self,
        model_key: str,
        device: str = "CPU",
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        self.model_key = model_key
        self.device = device
        self.progress_callback = progress_callback
        self.model_info = GENAI_MODELS.get(self.model_key, {})

        rel_path = self.model_info.get("local_path", f"genai/{self.model_key}")
        self.local_path = MODELS_DIR / rel_path

    def load(self) -> Any:
        import openvino_genai as ov_genai

        logger.info(
            "Loading OpenVINO GenAI model from %s to %s", self.local_path, self.device
        )

        if not self.local_path.exists():
            logger.info(
                "Model not found locally. Attempting to download from HuggingFace."
            )
            if self.progress_callback:
                self.progress_callback(
                    f"Downloading model '{self.model_info.get('name', self.model_key)}' from HuggingFace. This may take a few minutes..."
                )
            download_model(self.model_key)

        pipe = ov_genai.LLMPipeline(str(self.local_path), self.device)
        return pipe


def download_model(model_key: str) -> Path:
    """Download a GenAI model from HuggingFace."""
    model_info = GENAI_MODELS.get(model_key)
    if not model_info:
        raise ValueError(f"Unknown GenAI model key: {model_key}")

    hf_repo = model_info.get("hf_repo")
    local_rel_path = model_info.get("local_path", f"genai/{model_key}")

    if not hf_repo:
        raise ValueError(f"No HuggingFace repo configured for model: {model_key}")

    target_dir = MODELS_DIR / local_rel_path
    logger.info(
        "Downloading '%s' from '%s' to %s", model_info["name"], hf_repo, target_dir
    )

    target_dir.mkdir(parents=True, exist_ok=True)

    downloaded_path = snapshot_download(
        repo_id=hf_repo,
        local_dir=str(target_dir),
        ignore_patterns=[
            "*.onnx",
            "*.pt",
            "*.pth",
            "*.safetensors",
            "pytorch_model.bin",
            ".git*",
        ],
    )
    logger.info("Successfully downloaded model to %s", downloaded_path)
    return Path(downloaded_path)


def get_default_prompt() -> str:
    return "Explain the theory of relativity in 50 words:"
