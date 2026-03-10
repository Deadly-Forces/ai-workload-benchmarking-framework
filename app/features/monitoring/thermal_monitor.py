"""Thermal monitoring (best-effort, platform-dependent)."""
from __future__ import annotations

from typing import Optional
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def get_temperature() -> Optional[float]:
    """Get CPU temperature in Celsius. Returns None if unavailable."""
    try:
        import psutil
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        # Try common sensor names
        for name in ["coretemp", "cpu_thermal", "k10temp", "acpitz"]:
            if name in temps:
                readings = temps[name]
                if readings:
                    return readings[0].current
        # Fallback: use first available sensor
        for entries in temps.values():
            if entries:
                return entries[0].current
    except AttributeError:
        # sensors_temperatures not available on Windows
        pass
    except Exception as e:
        logger.debug("Thermal monitoring unavailable: %s", e)
    return None


def is_thermal_monitoring_available() -> bool:
    """Check if thermal monitoring is possible."""
    return get_temperature() is not None
