"""Enhancement inference logic."""
from __future__ import annotations

import numpy as np
from typing import Any

from app.config.constants import BACKEND_OPENVINO, BACKEND_ONNX


def run_inference(model: Any, input_tensor: np.ndarray, backend: str) -> np.ndarray:
    """Run super-resolution inference."""
    if backend == BACKEND_OPENVINO:
        infer_request = model.create_infer_request()
        infer_request.infer({0: input_tensor})
        return infer_request.get_output_tensor(0).data.copy()
    elif backend == BACKEND_ONNX:
        input_name = model.get_inputs()[0].name
        result = model.run(None, {input_name: input_tensor})
        return result[0]
    else:
        raise ValueError(f"Unsupported backend: {backend}")
