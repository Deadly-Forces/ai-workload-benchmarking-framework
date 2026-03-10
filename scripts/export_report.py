"""Export a report from previously stored results.

Usage:
    python scripts/export_report.py [--format json|csv]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.settings import EXPORTS_DIR, STORAGE_DIR
from app.config.logging_config import setup_logging, get_logger
from app.core.schemas import BenchmarkResult
from app.core.utils import load_json
from app.features.reporting.report_builder import build_report

setup_logging()
logger = get_logger(__name__)


def _load_results_from_storage() -> list[BenchmarkResult]:
    """Scan storage/runs/ for JSON result files and hydrate."""
    runs_dir = STORAGE_DIR / "runs"
    results = []
    if not runs_dir.exists():
        return results
    for fp in sorted(runs_dir.glob("*.json")):
        try:
            data = load_json(fp)
            # Minimal hydration — just enough for the report builder
            results.append(BenchmarkResult(**data))
        except Exception as e:
            logger.warning("Skipping %s: %s", fp.name, e)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Export benchmark report")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    args = parser.parse_args()

    results = _load_results_from_storage()
    if not results:
        logger.warning("No results found in storage. Run a benchmark first.")
        return

    paths = build_report(results, formats=[args.format])
    for fmt, p in paths.items():
        logger.info("Exported %s → %s", fmt, p)


if __name__ == "__main__":
    main()
