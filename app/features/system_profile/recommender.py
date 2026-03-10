"""Hardware configuration recommender for benchmarks."""

from __future__ import annotations

from typing import Dict, Any

from app.config.constants import (
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_GENAI,
    WORKLOAD_STRESS,
    BACKEND_ONNX,
    BACKEND_OPENVINO,
    DEVICE_CPU,
    DEVICE_GPU,
    CLASSIFICATION_MODELS,
    DETECTION_MODELS,
    ENHANCEMENT_MODELS,
    GENAI_MODELS,
)
from app.features.system_profile.schemas import SystemProfile


class RecommenderScore:
    """Helper to score different models based on hardware specs."""

    @staticmethod
    def get_max_model_size_mb(profile: SystemProfile) -> int:
        """Estimate maximum safe model size based on available memory."""
        # Use 75% of VRAM if a dedicated GPU is reporting memory
        if profile.gpu.available and profile.gpu.memory_mb:
            if profile.gpu.memory_mb > 0:
                return int(profile.gpu.memory_mb * 0.75)
        # Use 50% of available system RAM as a fallback
        return int((profile.memory.available_gb * 1024) * 0.50)


def get_recommended_config(profile: SystemProfile, workload: str) -> Dict[str, Any]:
    """
    Get recommended backend, device, and compatible models.

    Returns:
        dict: {
            "backend": "openvino" | "onnxruntime",
            "device": "CPU" | "GPU",
            "models": ["model1", "model2", ...],
            "default_model": "model1",
            "reasoning": "Explanation string"
        }
    """
    os_name = profile.os_name
    gpu = profile.gpu
    reasoning_parts = []

    # 1. Determine Backend & Device map
    backend = BACKEND_ONNX
    device = DEVICE_CPU

    if os_name == "Darwin":
        if gpu.available and gpu.vendor == "Apple":
            backend = BACKEND_ONNX
            device = DEVICE_CPU  # MPS/CoreML is handled under the hood in ONNX Runtime ORT if configured
            reasoning_parts.append(
                "Apple Silicon detected: using ONNX (CPU/CoreML backend)."
            )
        else:
            backend = BACKEND_ONNX
            device = DEVICE_CPU
            reasoning_parts.append("macOS Intel detected: using ONNX (CPU).")
    else:  # Windows or Linux
        if gpu.available:
            if gpu.vendor == "Intel":
                backend = BACKEND_OPENVINO
                device = DEVICE_GPU
                reasoning_parts.append(
                    f"Intel GPU ({gpu.name}) detected: using OpenVINO for optimal performance."
                )
            elif gpu.vendor == "NVIDIA":
                backend = BACKEND_ONNX
                device = DEVICE_GPU
                reasoning_parts.append(
                    f"NVIDIA GPU ({gpu.name}) detected: using ONNX Runtime (CUDA)."
                )
            elif gpu.vendor == "AMD":
                backend = BACKEND_ONNX
                device = DEVICE_GPU
                reasoning_parts.append(
                    f"AMD GPU ({gpu.name}) detected: using ONNX Runtime (DirectML/ROCm)."
                )
            else:
                backend = BACKEND_ONNX
                device = DEVICE_GPU
                reasoning_parts.append(
                    f"Generic GPU ({gpu.name}) detected: using ONNX Runtime (GPU)."
                )
        else:
            if profile.cpu.vendor == "Intel" or "intel" in profile.cpu.name.lower():
                backend = BACKEND_OPENVINO
                device = DEVICE_CPU
                reasoning_parts.append(
                    "Intel CPU detected: using OpenVINO for CPU optimization."
                )
            else:
                backend = BACKEND_ONNX
                device = DEVICE_CPU
                reasoning_parts.append("Fallback to ONNX Runtime on CPU.")

    # 2. Check if OpenVINO backend was selected but not installed/available
    if backend == BACKEND_OPENVINO and not profile.inference_devices.openvino_devices:
        backend = BACKEND_ONNX
        reasoning_parts.append(
            "OpenVINO not installed/detected. Falling back to ONNX Runtime."
        )

    # 3. Determine models appropriate for workload
    model_keys = []
    default_model = None

    if workload == WORKLOAD_CLASSIFICATION:
        models_dict = CLASSIFICATION_MODELS
    elif workload == WORKLOAD_DETECTION:
        models_dict = DETECTION_MODELS
    elif workload == WORKLOAD_ENHANCEMENT:
        models_dict = ENHANCEMENT_MODELS
    elif workload == WORKLOAD_GENAI:
        models_dict = GENAI_MODELS
    elif workload == WORKLOAD_STRESS:
        models_dict = CLASSIFICATION_MODELS
    else:
        models_dict = {}

    max_size_mb = RecommenderScore.get_max_model_size_mb(profile)

    # Filter models based on backend availability and memory (heuristic)
    for mk, v in models_dict.items():
        # Validate backend compatibility
        if (
            backend == BACKEND_OPENVINO
            and "openvino_model" not in v
            and "hf_repo" not in v
        ):
            continue
        if backend == BACKEND_ONNX and "onnx_model" not in v and "hf_repo" not in v:
            continue

        # Check memory bounds based on required_ram_mb
        req_ram = v.get("required_ram_mb", 0)
        if max_size_mb < req_ram:
            continue

        model_keys.append(mk)

    if not model_keys and models_dict:
        # Fallback if filters are too strict (e.g., system is too weak for even the smallest model)
        # Find the model with the minimum required_ram_mb
        smallest_model_key = min(
            models_dict.keys(),
            key=lambda k: models_dict[k].get("required_ram_mb", float("inf")),
        )
        model_keys.append(smallest_model_key)
        reasoning_parts.append(
            f"System memory ({max_size_mb} MB) is below recommended limits. Defaulting to smallest fallback model."
        )

    if model_keys:
        # Sort model_keys descending by required_ram_mb so the most powerful capable model is the default
        model_keys.sort(
            key=lambda mk: models_dict[mk].get("required_ram_mb", 0), reverse=True
        )
        default_model = model_keys[0]

    return {
        "backend": backend,
        "device": device,
        "models": model_keys,
        "default_model": default_model,
        "reasoning": " ".join(reasoning_parts),
    }
