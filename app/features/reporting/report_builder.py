"""Report builder — high-level report assembly from results."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.config.logging_config import get_logger
from app.config.settings import EXPORTS_DIR
from app.core.schemas import BenchmarkResult
from app.core.utils import generate_run_id, timestamp_now
from app.features.analysis.scoring import compute_score
from app.features.reporting.export_json import export_result_json, export_results_json
from app.features.reporting.export_csv import export_results_csv

logger = get_logger(__name__)


def build_report(
    results: List[BenchmarkResult],
    *,
    export_dir: Optional[Path] = None,
    formats: Optional[List[str]] = None,
) -> Dict[str, Path]:
    """Build and export reports in the requested formats.

    Returns a dict mapping format name → output path.
    """
    out_dir = Path(export_dir or EXPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = timestamp_now().replace(":", "-")
    formats = formats or ["json", "csv"]
    exported: dict[str, Path] = {}

    if "json" in formats:
        p = out_dir / f"report_{ts}.json"
        export_results_json(results, p)
        exported["json"] = p

    if "csv" in formats:
        p = out_dir / f"report_{ts}.csv"
        export_results_csv(results, p)
        exported["csv"] = p

    logger.info("Report exported: %s", list(exported.keys()))
    return exported
