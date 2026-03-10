"""Shared utility functions."""
from __future__ import annotations

import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def generate_run_id() -> str:
    """Generate a unique benchmark run identifier."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"run_{ts}_{short_uuid}"


def timestamp_now() -> str:
    """Return an ISO-format UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def safe_json_serialize(obj: Any) -> Any:
    """Make objects JSON-safe by converting non-serializable types."""
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "__dict__"):
        return {k: safe_json_serialize(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [safe_json_serialize(i) for i in obj]
    return obj


def save_json(data: Any, path: Path) -> None:
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(safe_json_serialize(data), f, indent=2, default=str)


def load_json(path: Path) -> Any:
    """Load JSON data from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f} µs"
    if seconds < 1.0:
        return f"{seconds * 1_000:.2f} ms"
    if seconds < 60.0:
        return f"{seconds:.2f} s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def format_throughput(fps: float) -> str:
    """Format throughput as inferences per second."""
    if fps >= 1000:
        return f"{fps:.0f} inf/s"
    if fps >= 1:
        return f"{fps:.1f} inf/s"
    return f"{fps:.3f} inf/s"
