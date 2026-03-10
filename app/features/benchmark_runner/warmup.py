"""Warmup utilities for benchmark runs."""
from __future__ import annotations

from typing import Callable
from app.config.logging_config import get_logger
from app.core.timer import PrecisionTimer

logger = get_logger(__name__)


def run_warmup(
    inference_fn: Callable[[], None],
    warmup_count: int,
) -> float:
    """Execute warmup iterations and return total warmup time in seconds."""
    logger.info("Running %d warmup iterations...", warmup_count)
    total = 0.0
    for i in range(warmup_count):
        with PrecisionTimer(f"warmup_{i}") as t:
            inference_fn()
        total += t.elapsed
    logger.info("Warmup complete (%.2fs total)", total)
    return total
