"""Natural Language Intent Parser for Benchmarking."""

from __future__ import annotations

import ssl
from typing import Dict, Any

from app.config.logging_config import get_logger
from app.config.constants import (
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_STRESS,
    WORKLOAD_GENAI,
    DEVICE_CPU,
    DEVICE_GPU,
    BACKEND_OPENVINO,
    BACKEND_ONNX,
)

logger = get_logger(__name__)

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Intent parsing is disabled.")

# Handle SSL issues during model download
# pylint: disable=protected-access
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
# pylint: enable=protected-access


class IntentParser:
    """Parses natural language to standard benchmark configurations."""

    # Class-level cache to avoid reloading pipeline
    _classifier = None

    def __init__(self):
        self.is_ready = False
        if TRANSFORMERS_AVAILABLE:
            if IntentParser._classifier is None:
                try:
                    logger.info("Loading DistilBERT zero-shot classifier...")
                    # Using a smaller zero-shot model for faster local execution
                    IntentParser._classifier = pipeline(
                        "zero-shot-classification",
                        model="typeform/distilbert-base-uncased-mnli",
                    )
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("Failed to load intent parser: %s", e)

            if IntentParser._classifier is not None:
                self.is_ready = True

    def parse_user_intent(self, text: str) -> Dict[str, Any]:
        """Parse user chat message into structured config fields."""
        result = {
            "workload_type": WORKLOAD_CLASSIFICATION,  # default
            "device": DEVICE_CPU,
            "backend": BACKEND_OPENVINO,
        }

        if not self.is_ready or not text:
            return result

        text = text.lower()

        # 1. Determine Workload Type using Zero-Shot
        workload_labels = [
            "classification",
            "detection",
            "enhancement",
            "generative ai",
            "stress test",
        ]
        try:
            # pylint: disable=not-callable
            wl_res = IntentParser._classifier(text, workload_labels)
            # pylint: enable=not-callable
            top_workload = wl_res["labels"][0]
            score = wl_res["scores"][0]
            logger.info(
                "Parsed workload '%s' with confidence %.2f", top_workload, score
            )

            if score > 0.4:  # Confidence threshold
                if top_workload == "classification":
                    result["workload_type"] = WORKLOAD_CLASSIFICATION
                elif top_workload == "detection":
                    result["workload_type"] = WORKLOAD_DETECTION
                elif top_workload == "enhancement":
                    result["workload_type"] = WORKLOAD_ENHANCEMENT
                elif top_workload == "generative ai":
                    result["workload_type"] = WORKLOAD_GENAI
                elif top_workload == "stress test":
                    result["workload_type"] = WORKLOAD_STRESS
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Workload parsing failed: %s", e)

        # 2. Heuristic extraction for hardware & backend
        if "gpu" in text or "iris xe" in text or "iris" in text:
            result["device"] = DEVICE_GPU

        if "onnx" in text:
            result["backend"] = BACKEND_ONNX

        return result


# Singleton helper
_PARSER_INSTANCE = None


def get_intent_parser() -> IntentParser:
    """Get the singleton instance of IntentParser."""
    global _PARSER_INSTANCE  # pylint: disable=global-statement
    if _PARSER_INSTANCE is None:
        _PARSER_INSTANCE = IntentParser()
    return _PARSER_INSTANCE
