"""Verify what CPU/GPU the profiler detects and what model the recommender picks."""

import sys
import os

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.features.system_profile.profiler import build_system_profile
from app.features.system_profile.recommender import get_recommended_config
from app.config.constants import WORKLOAD_GENAI

print("")
print("==================================")
print("  LIVE SYSTEM HARDWARE DETECTION")
print("==================================")
print("")

profile = build_system_profile()

print("OS:     " + profile.os_name + " " + profile.os_version)
print(
    "Memory: "
    + str(round(profile.memory.total_gb, 1))
    + " GB Total / "
    + str(round(profile.memory.available_gb, 1))
    + " GB Available"
)
print(
    "CPU:    "
    + profile.cpu.name
    + " ("
    + str(profile.cpu.cores_physical)
    + " physical cores)"
)

if profile.gpu.available:
    vram = str(profile.gpu.memory_mb) if profile.gpu.memory_mb else "N/A"
    print(
        "GPU:    "
        + profile.gpu.name
        + " ("
        + profile.gpu.vendor
        + ") - "
        + vram
        + " MB VRAM"
    )
else:
    print("GPU:    None detected or unavailable")

print("")
print("==================================")
print("  GENAI MODEL RECOMMENDATION")
print("==================================")
print("")

genai_rec = get_recommended_config(profile, WORKLOAD_GENAI)

print("Backend:  " + genai_rec["backend"])
print("Device:   " + genai_rec["device"])
print("Reasoning: " + genai_rec["reasoning"])
print("")
print("Compatible Models (sorted by capability):")
for m in genai_rec["models"]:
    print("  - " + m)
print("")
print("Default Selected Model: " + str(genai_rec["default_model"]))
print("")
