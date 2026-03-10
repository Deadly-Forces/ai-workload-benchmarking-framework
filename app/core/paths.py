"""Path resolution helpers."""
from pathlib import Path
from app.config.settings import MODELS_DIR, DATASETS_DIR, BENCHMARK_RUNS_DIR, EXPORTS_DIR


def model_path(relative: str) -> Path:
    """Resolve a model file path relative to the models directory."""
    return MODELS_DIR / relative


def dataset_path(relative: str) -> Path:
    """Resolve a dataset file path relative to the datasets directory."""
    return DATASETS_DIR / relative


def run_path(filename: str) -> Path:
    """Resolve a benchmark run file path."""
    return BENCHMARK_RUNS_DIR / filename


def export_path(filename: str) -> Path:
    """Resolve an export file path."""
    return EXPORTS_DIR / filename


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
