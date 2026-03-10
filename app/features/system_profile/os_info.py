"""OS information detection."""
import platform
import sys


def get_os_name() -> str:
    """Get OS name."""
    return platform.system()


def get_os_version() -> str:
    """Get OS version string."""
    return platform.version()


def get_platform_string() -> str:
    """Get full platform string."""
    return platform.platform()


def get_python_version() -> str:
    """Get Python version string."""
    return sys.version.split()[0]


def get_architecture() -> str:
    """Get system architecture."""
    return platform.machine()
