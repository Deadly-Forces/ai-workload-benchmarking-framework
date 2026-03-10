"""Custom exception hierarchy."""


class BenchmarkError(Exception):
    """Base exception for benchmark-related errors."""


class ModelLoadError(BenchmarkError):
    """Raised when a model cannot be loaded."""


class InferenceError(BenchmarkError):
    """Raised when inference fails."""


class DeviceNotAvailableError(BenchmarkError):
    """Raised when the requested device is not available."""


class DatasetError(BenchmarkError):
    """Raised when dataset loading or validation fails."""


class ExportError(BenchmarkError):
    """Raised when export operation fails."""


class MonitoringError(BenchmarkError):
    """Raised when monitoring fails (non-critical)."""
