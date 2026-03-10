"""CPU usage monitor."""
import psutil


def get_cpu_percent(interval: float = 0.0) -> float:
    """Get current CPU usage percentage."""
    return psutil.cpu_percent(interval=interval)


def get_per_cpu_percent() -> list:
    """Get per-core CPU usage."""
    return psutil.cpu_percent(percpu=True)
