"""System profiler — aggregates all system information."""

from __future__ import annotations

import psutil

from app.core.utils import timestamp_now
from app.config.logging_config import get_logger
from app.features.system_profile.schemas import (
    CPUInfo,
    GPUInfo,
    MemoryInfo,
    InferenceDevices,
    SystemProfile,
)
from app.features.system_profile.os_info import (
    get_os_name,
    get_os_version,
    get_python_version,
    get_architecture,
)
from app.features.system_profile.device_detector import (
    detect_openvino_devices,
    detect_onnx_providers,
)

logger = get_logger(__name__)


def get_cpu_info() -> CPUInfo:
    """Collect CPU information."""
    info = CPUInfo()
    try:
        import cpuinfo

        ci = cpuinfo.get_cpu_info()
        info.name = ci.get("brand_raw", "Unknown CPU")
        info.architecture = ci.get("arch", get_architecture())
    except Exception:
        info.name = "Unknown CPU"
        info.architecture = get_architecture()

    # macOS specific check for Apple Silicon name
    if get_os_name() == "Darwin":
        try:
            import subprocess

            res = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if res.returncode == 0 and res.stdout.strip():
                info.name = res.stdout.strip()
        except Exception:
            pass

    info.cores_physical = psutil.cpu_count(logical=False) or 0
    info.cores_logical = psutil.cpu_count(logical=True) or 0
    freq = psutil.cpu_freq()
    if freq:
        info.frequency_mhz = freq.current
    return info


def get_gpu_info() -> GPUInfo:
    """Collect GPU information (best effort)."""
    info = GPUInfo()

    # Try GPUtil first (for discrete NVIDIA GPUs)
    try:
        import GPUtil

        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            info.name = gpu.name
            info.memory_mb = gpu.memoryTotal
            info.available = True
            info.driver_version = gpu.driver
            info.vendor = "NVIDIA"
            return info
    except Exception:
        pass

    os_name = get_os_name()
    if os_name == "Windows":
        # PowerShell / CIM fallback (works on modern Windows without wmic)
        try:
            import subprocess, json

            ps_cmd = (
                "Get-CimInstance Win32_VideoController "
                "| Select-Object Name, DriverVersion, AdapterRAM "
                "| ConvertTo-Json"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                # CIM may return a single dict or a list
                entries = data if isinstance(data, list) else [data]
                for entry in entries:
                    name = entry.get("Name", "")
                    if not name:
                        continue
                    info.name = name
                    info.driver_version = entry.get("DriverVersion", "")
                    adapter_ram = entry.get("AdapterRAM")
                    if adapter_ram:
                        info.memory_mb = round(int(adapter_ram) / (1024 * 1024))
                    info.available = True
                    name_lower = name.lower()
                    if "intel" in name_lower:
                        info.vendor = "Intel"
                    elif "nvidia" in name_lower:
                        info.vendor = "NVIDIA"
                    elif "amd" in name_lower or "radeon" in name_lower:
                        info.vendor = "AMD"
                    return info
        except Exception:
            pass
    elif os_name == "Linux":
        try:
            import subprocess

            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "VGA compatible controller" in line or "3D controller" in line:
                        info.name = line.split(": ")[-1].strip()
                        info.available = True
                        name_lower = info.name.lower()
                        if "intel" in name_lower:
                            info.vendor = "Intel"
                        elif "nvidia" in name_lower:
                            info.vendor = "NVIDIA"
                        elif "amd" in name_lower or "radeon" in name_lower:
                            info.vendor = "AMD"
                        return info
        except Exception:
            pass
    elif os_name == "Darwin":
        try:
            import subprocess

            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                for line in lines:
                    if "Chipset Model:" in line:
                        info.name = line.split(":")[1].strip()
                        info.available = True
                        if "apple" in info.name.lower():
                            info.vendor = "Apple"
                        elif "intel" in info.name.lower():
                            info.vendor = "Intel"
                        elif (
                            "amd" in info.name.lower() or "radeon" in info.name.lower()
                        ):
                            info.vendor = "AMD"
                    elif "VRAM" in line and info.available:
                        # e.g., "VRAM (Total): 16 GB" or "VRAM (Dynamic, Max): 8 GB"
                        try:
                            parts = line.split(":")[-1].strip().split()
                            val = parts[0]
                            unit = parts[1].upper() if len(parts) > 1 else "MB"
                            memory_mb = float(val)
                            if unit == "GB":
                                memory_mb *= 1024
                            info.memory_mb = int(memory_mb)
                        except Exception:
                            pass
                if info.available:
                    return info
        except Exception:
            pass

    info.name = "Not detected"
    info.available = False
    return info


def get_memory_info() -> MemoryInfo:
    """Collect memory information."""
    mem = psutil.virtual_memory()
    return MemoryInfo(
        total_gb=round(mem.total / (1024**3), 2),
        available_gb=round(mem.available / (1024**3), 2),
        percent_used=mem.percent,
    )


def assess_suitability(profile: SystemProfile) -> dict:
    """Assess hardware suitability for AI benchmarking."""
    suitability = {}

    # CPU assessment
    if profile.cpu.cores_logical >= 4:
        suitability["cpu"] = {
            "rating": "Good",
            "note": f"{profile.cpu.cores_logical} logical cores",
        }
    else:
        suitability["cpu"] = {
            "rating": "Limited",
            "note": f"Only {profile.cpu.cores_logical} cores",
        }

    # Memory assessment
    if profile.memory.total_gb >= 16:
        suitability["memory"] = {
            "rating": "Excellent",
            "note": f"{profile.memory.total_gb} GB RAM",
        }
    elif profile.memory.total_gb >= 8:
        suitability["memory"] = {
            "rating": "Good",
            "note": f"{profile.memory.total_gb} GB RAM",
        }
    else:
        suitability["memory"] = {
            "rating": "Limited",
            "note": f"{profile.memory.total_gb} GB RAM",
        }

    # GPU assessment
    if profile.gpu.available:
        if "iris xe" in profile.gpu.name.lower():
            suitability["gpu"] = {
                "rating": "Supported",
                "note": "Intel Iris Xe (OpenVINO optimized)",
            }
        elif "intel" in profile.gpu.name.lower():
            suitability["gpu"] = {
                "rating": "Supported",
                "note": f"{profile.gpu.name} (Intel iGPU)",
            }
        else:
            suitability["gpu"] = {"rating": "Good", "note": profile.gpu.name}
    else:
        suitability["gpu"] = {"rating": "CPU Only", "note": "No GPU detected"}

    # OpenVINO assessment
    if profile.inference_devices.openvino_devices:
        devices = ", ".join(profile.inference_devices.openvino_devices)
        suitability["openvino"] = {"rating": "Available", "note": f"Devices: {devices}"}
    else:
        if profile.gpu.available and profile.gpu.vendor == "Intel":
            suitability["openvino"] = {
                "rating": "Recommended",
                "note": "Install OpenVINO for Intel GPU acceleration",
            }
        else:
            suitability["openvino"] = {
                "rating": "Not Installed",
                "note": "Optional — ONNX Runtime is active",
            }

    return suitability


def build_system_profile() -> SystemProfile:
    """Build a complete system profile."""
    logger.info("Building system profile...")
    profile = SystemProfile(
        cpu=get_cpu_info(),
        gpu=get_gpu_info(),
        memory=get_memory_info(),
        os_name=get_os_name(),
        os_version=get_os_version(),
        python_version=get_python_version(),
        inference_devices=InferenceDevices(
            openvino_devices=detect_openvino_devices(),
            onnx_providers=detect_onnx_providers(),
        ),
        timestamp=timestamp_now(),
    )
    profile.suitability = assess_suitability(profile)
    logger.info("System profile built successfully")
    return profile
