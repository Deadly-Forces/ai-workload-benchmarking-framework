"""Detection benchmark schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Detection:
    """A single detected object."""
    class_id: int = 0
    label: str = ""
    confidence: float = 0.0
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0


@dataclass
class DetectionOutput:
    """Output from detection inference."""
    detections: List[Detection] = field(default_factory=list)
    num_detections: int = 0
