"""GPU usage monitor (best-effort)."""
from __future__ import annotations

from typing import Optional, Tuple
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def get_gpu_usage() -> Tuple[Optional[float], Optional[float]]:
    """Get GPU utilization and memory usage. Returns (percent, memory_mb) or (None, None)."""
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return gpu.load * 100.0, gpu.memoryUsed
    except ImportError:
        pass
    except Exception as e:
        logger.debug("GPU monitoring unavailable: %s", e)
    return None, None


def is_gpu_monitoring_available() -> bool:
    """Check if GPU monitoring is possible."""
    usage, _ = get_gpu_usage()
    return usage is not None
