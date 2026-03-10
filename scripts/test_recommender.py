import sys
from pathlib import Path

# Setup project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.features.system_profile.schemas import (
    SystemProfile,
    CPUInfo,
    GPUInfo,
    MemoryInfo,
    InferenceDevices,
)
from app.features.system_profile.recommender import get_recommended_config
from app.config.constants import WORKLOAD_GENAI


def make_profile(ram_gb, vram_mb):
    return SystemProfile(
        os_name="Windows",
        os_version="10",
        cpu=CPUInfo(name="Intel i7", architecture="x86_64", cores_physical=8),
        gpu=GPUInfo(
            available=True,
            name="Intel Arc",
            vendor="Intel",
            driver_version="1.0",
            memory_mb=vram_mb,
        ),
        memory=MemoryInfo(total_gb=ram_gb, available_gb=ram_gb, percent_used=0),
        inference_devices=InferenceDevices(
            openvino_devices=["CPU", "GPU"], onnx_providers=["CPUExecutionProvider"]
        ),
    )


print("--- Testing 16GB RAM / 8GB VRAM System ---")
p1 = make_profile(16.0, 8000)
res1 = get_recommended_config(p1, WORKLOAD_GENAI)
print(f"Models: {res1['models']}")
print(f"Default: {res1['default_model']}")
print(f"Reasoning: {res1['reasoning']}")

print("\n--- Testing 8GB RAM / 2GB VRAM System ---")
p2 = make_profile(8.0, 2000)
res2 = get_recommended_config(p2, WORKLOAD_GENAI)
print(f"Models: {res2['models']}")
print(f"Default: {res2['default_model']}")
print(f"Reasoning: {res2['reasoning']}")

print("\n--- Testing 4GB RAM / 512MB VRAM System (Too weak!) ---")
p3 = make_profile(4.0, 512)
res3 = get_recommended_config(p3, WORKLOAD_GENAI)
print(f"Models: {res3['models']}")
print(f"Default: {res3['default_model']}")
print(f"Reasoning: {res3['reasoning']}")
