"""System profile schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CPUInfo:
    """CPU information."""
    name: str = "Unknown"
    cores_physical: int = 0
    cores_logical: int = 0
    frequency_mhz: float = 0.0
    architecture: str = ""


@dataclass
class GPUInfo:
    """GPU information."""
    name: str = "Unknown"
    vendor: str = ""
    driver_version: str = ""
    memory_mb: Optional[float] = None
    available: bool = False


@dataclass
class MemoryInfo:
    """System memory information."""
    total_gb: float = 0.0
    available_gb: float = 0.0
    percent_used: float = 0.0


@dataclass
class InferenceDevices:
    """Available inference devices."""
    openvino_devices: List[str] = field(default_factory=list)
    onnx_providers: List[str] = field(default_factory=list)


@dataclass
class SystemProfile:
    """Complete system profile."""
    cpu: CPUInfo = field(default_factory=CPUInfo)
    gpu: GPUInfo = field(default_factory=GPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    os_name: str = ""
    os_version: str = ""
    python_version: str = ""
    inference_devices: InferenceDevices = field(default_factory=InferenceDevices)
    suitability: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        from app.core.utils import safe_json_serialize
        return safe_json_serialize(self.__dict__)
