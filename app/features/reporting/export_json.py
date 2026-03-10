"""Export benchmark results to JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.core.utils import safe_json_serialize

logger = get_logger(__name__)


def export_result_json(result: BenchmarkResult, path: Path) -> Path:
    """Write a single BenchmarkResult as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = safe_json_serialize(result.__dict__)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    logger.info("Exported JSON → %s", path)
    return path


def export_results_json(results: List[BenchmarkResult], path: Path) -> Path:
    """Write a list of BenchmarkResults as a JSON array."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [safe_json_serialize(r.__dict__) for r in results]
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    logger.info("Exported %d results → %s", len(results), path)
    return path
