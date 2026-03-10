"""Enhancement benchmark schemas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class EnhancementOutput:
    """Output from enhancement inference."""
    psnr: Optional[float] = None
    ssim: Optional[float] = None
    scale_factor: int = 2
    output_height: int = 0
    output_width: int = 0
