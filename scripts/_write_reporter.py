"""Helper to write the ai_reporter.py file with correct special chars."""

import pathlib

target = pathlib.Path(
    r"E:\Programming\Projects\GPGPU PROJECT\ai-workload-benchmarking-framework"
    r"\app\features\analysis\ai_reporter.py"
)

SYS_TAG = "<" + "|system|" + ">"
USR_TAG = "<" + "|user|" + ">"
AST_TAG = "<" + "|assistant|" + ">"

CODE = f'''"""AI-generated performance reports."""

from __future__ import annotations

import json
from typing import Optional, Any

from app.config.logging_config import get_logger
from app.core.schemas import BenchmarkResult
from app.features.genai.model_utils import GenAIModelLoader

logger = get_logger(__name__)

# Cache the model pipeline so we don't reload it every time viewing results
_LLM_PIPELINE = None


def _get_llm_pipeline() -> Optional[Any]:
    """Lazy load the TinyLlama model for reporting."""
    global _LLM_PIPELINE  # pylint: disable=global-statement
    if _LLM_PIPELINE is not None:
        return _LLM_PIPELINE

    try:
        loader = GenAIModelLoader(model_key="tinyllama-1.1b-chat", device="CPU")
        _LLM_PIPELINE = loader.load()
        return _LLM_PIPELINE
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to load AI Reporter model: %s", e)
        return None


def _clean_generated_text(text: str) -> str:
    """Post-process generated text to remove incomplete trailing sentences."""
    text = text.strip()
    if not text:
        return text

    # If the text ends with a complete sentence, return as-is
    if text[-1] in ".!?":
        return text

    # Otherwise, trim to the last complete sentence
    for i in range(len(text) - 1, -1, -1):
        if text[i] in ".!?":
            return text[: i + 1]

    # If no sentence-ending punctuation found at all, return what we have
    return text


def generate_insight_report(result: BenchmarkResult) -> str:
    """Generate a human-readable performance report from a benchmark result."""
    pipeline = _get_llm_pipeline()
    if pipeline is None:
        return (
            "Local AI reporting model is unavailable. "
            "Please download GenAI models using scripts/download_genai_models.py."
        )

    # Create a dense but small summary of the metrics for the LLM
    data_summary = {{
        "workload": result.workload_type,
        "model": result.model_name,
        "device": result.device,
        "latency_ms": round(result.latency.avg_ms, 2),
        "fps": round(result.throughput_fps, 2),
        "cpu_usage": round(result.resource_usage.avg_cpu_percent, 1),
        "peak_ram_mb": round(result.resource_usage.max_memory_mb, 1),
    }}

    if result.thermal.available:
        data_summary["avg_temp_c"] = round(result.thermal.avg_temp_c, 1)

    metrics_json = json.dumps(data_summary)

    system_msg = (
        "You are an expert hardware and AI performance analyst. "
        "Given benchmark metrics, write a clear and complete 2-3 sentence summary. "
        "State whether performance is good or poor, highlight bottlenecks "
        "(high RAM, CPU, thermal throttling), and give one recommendation. "
        "Always finish every sentence completely."
    )

    prompt = (
        "{SYS_TAG}\\n"
        + system_msg
        + "\\n{USR_TAG}\\n"
        + "Metrics: " + metrics_json
        + "\\n{AST_TAG}\\n"
    )

    try:
        import openvino_genai as ov_genai

        config = ov_genai.GenerationConfig()
        config.max_new_tokens = 300

        logger.info("Generating AI Insight Report...")
        generated_text = pipeline.generate(prompt, config)
        return _clean_generated_text(generated_text)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Generation failed: %s", e)
        return "Failed to generate AI report: " + str(e)
'''

target.write_text(CODE, encoding="utf-8")
print(f"Successfully wrote {len(CODE)} chars to {target}")
