"""Classification benchmark schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ClassificationPrediction:
    """A single classification prediction."""
    label: str = ""
    class_id: int = 0
    confidence: float = 0.0


@dataclass
class ClassificationOutput:
    """Output from classification inference."""
    top_predictions: List[ClassificationPrediction] = field(default_factory=list)
    raw_scores: Optional[list] = None
