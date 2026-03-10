"""Application settings loaded from environment and defaults."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
APP_DIR = PROJECT_ROOT / "app"
MODELS_DIR = Path(os.getenv("BENCHMARK_MODELS_DIR", str(PROJECT_ROOT / "models")))
DATASETS_DIR = Path(os.getenv("BENCHMARK_DATASETS_DIR", str(PROJECT_ROOT / "datasets")))
STORAGE_DIR = Path(os.getenv("BENCHMARK_STORAGE_DIR", str(PROJECT_ROOT / "storage")))
BENCHMARK_RUNS_DIR = STORAGE_DIR / "runs"
EXPORTS_DIR = STORAGE_DIR / "exports"
CACHE_DIR = STORAGE_DIR / "cache"

# ── Logging ────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ── Benchmark defaults ─────────────────────────────────────────────────
DEFAULT_ITERATIONS = int(os.getenv("DEFAULT_ITERATIONS", "20"))
DEFAULT_WARMUP = int(os.getenv("DEFAULT_WARMUP", "5"))
DEFAULT_BATCH_SIZE = int(os.getenv("DEFAULT_BATCH_SIZE", "1"))
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", "100"))
STRESS_DURATION_SECONDS = int(os.getenv("STRESS_DURATION_SECONDS", "60"))

# ── Storage ────────────────────────────────────────────────────────────
MAX_STORED_RUNS = int(os.getenv("MAX_STORED_RUNS", "100"))

# ── OpenVINO ───────────────────────────────────────────────────────────
OPENVINO_DEVICE = os.getenv("OPENVINO_DEVICE", "AUTO")

# ── Ensure directories exist ──────────────────────────────────────────
for d in [MODELS_DIR, DATASETS_DIR, BENCHMARK_RUNS_DIR, EXPORTS_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)
