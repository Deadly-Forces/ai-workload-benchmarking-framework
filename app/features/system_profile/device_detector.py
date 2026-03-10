"""Inference device detection for OpenVINO and ONNX Runtime."""
from __future__ import annotations

from typing import List
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def detect_openvino_devices() -> List[str]:
    """Detect available OpenVINO inference devices."""
    try:
        from openvino import Core  # type: ignore[import-not-found]
        core = Core()
        devices = core.available_devices
        logger.info("OpenVINO devices detected: %s", devices)
        return list(devices)
    except ImportError:
        logger.warning("OpenVINO not installed")
        return []
    except Exception as e:
        logger.warning("Failed to detect OpenVINO devices: %s", e)
        return []


def detect_onnx_providers() -> List[str]:
    """Detect available ONNX Runtime execution providers."""
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        logger.info("ONNX Runtime providers: %s", providers)
        return providers
    except ImportError:
        logger.warning("ONNX Runtime not installed")
        return []
    except Exception as e:
        logger.warning("Failed to detect ONNX providers: %s", e)
        return []


def is_gpu_available_openvino() -> bool:
    """Check if GPU device is available in OpenVINO."""
    devices = detect_openvino_devices()
    return "GPU" in devices


def is_gpu_available_onnx() -> bool:
    """Check if a GPU execution provider is available in ONNX Runtime."""
    providers = detect_onnx_providers()
    gpu_providers = {"CUDAExecutionProvider", "DmlExecutionProvider", "OpenVINOExecutionProvider"}
    return bool(gpu_providers & set(providers))
