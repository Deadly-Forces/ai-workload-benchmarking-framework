"""Schemas specific to GenAI workloads."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GenMetrics:
    """Metrics for language generation."""

    ttft_ms: float = 0.0
    tps: float = 0.0
    generated_text: str = ""
    prompt_tokens: int = 0
    generated_tokens: int = 0
