"""Classification inference logic."""
from __future__ import annotations

import numpy as np
from typing import Any, List

from app.config.constants import BACKEND_OPENVINO, BACKEND_ONNX
from app.config.logging_config import get_logger
from app.features.classification.schemas import ClassificationPrediction, ClassificationOutput

logger = get_logger(__name__)


def run_openvino_inference(compiled_model: Any, input_tensor: np.ndarray) -> np.ndarray:
    """Run inference using an OpenVINO compiled model."""
    infer_request = compiled_model.create_infer_request()
    infer_request.infer({0: input_tensor})
    output = infer_request.get_output_tensor(0)
    return output.data.copy()


def run_onnx_inference(session: Any, input_tensor: np.ndarray) -> np.ndarray:
    """Run inference using an ONNX Runtime session."""
    input_name = session.get_inputs()[0].name
    result = session.run(None, {input_name: input_tensor})
    return result[0]


def run_inference(
    model: Any,
    input_tensor: np.ndarray,
    backend: str,
) -> np.ndarray:
    """Run inference using the specified backend."""
    if backend == BACKEND_OPENVINO:
        return run_openvino_inference(model, input_tensor)
    elif backend == BACKEND_ONNX:
        return run_onnx_inference(model, input_tensor)
    else:
        raise ValueError(f"Unsupported backend: {backend}")


def decode_predictions(
    output: np.ndarray,
    labels: List[str],
    top_k: int = 5,
) -> ClassificationOutput:
    """Decode raw model output into classification predictions."""
    # Apply softmax
    scores = output.flatten()
    exp_scores = np.exp(scores - np.max(scores))
    probs = exp_scores / exp_scores.sum()

    top_indices = np.argsort(probs)[::-1][:top_k]
    predictions = []
    for idx in top_indices:
        label = labels[idx] if idx < len(labels) else f"class_{idx}"
        predictions.append(ClassificationPrediction(
            label=label,
            class_id=int(idx),
            confidence=float(probs[idx]),
        ))

    return ClassificationOutput(
        top_predictions=predictions,
        raw_scores=probs.tolist(),
    )
