"""Memory usage monitor."""
import psutil


def get_memory_percent() -> float:
    """Get overall memory usage percentage."""
    return psutil.virtual_memory().percent


def get_memory_used_mb() -> float:
    """Get used memory in MB."""
    return psutil.virtual_memory().used / (1024 ** 2)


def get_process_memory_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 ** 2)
