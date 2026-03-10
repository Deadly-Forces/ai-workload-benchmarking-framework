"""Benchmark configuration form — sidebar or inline form for setting up a run."""

from __future__ import annotations

from typing import Tuple, Optional

import streamlit as st

from app.config.constants import (
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_STRESS,
    WORKLOAD_GENAI,
    BACKEND_OPENVINO,
    BACKEND_ONNX,
    DEVICE_CPU,
    DEVICE_GPU,
    CLASSIFICATION_MODELS,
    DETECTION_MODELS,
    ENHANCEMENT_MODELS,
    GENAI_MODELS,
    ALL_STRESS_TARGETS,
    STRESS_TARGET_LABELS,
)
from app.config.settings import (
    DEFAULT_ITERATIONS,
    DEFAULT_WARMUP,
    DEFAULT_BATCH_SIZE,
    STRESS_DURATION_SECONDS,
)
from app.features.benchmark_runner.schemas import BenchmarkConfig
from app.features.system_profile.profiler import build_system_profile
from app.features.system_profile.recommender import get_recommended_config


@st.cache_data(ttl=3600)
def _get_cached_profile():
    return build_system_profile()


_WORKLOAD_MODELS = {
    WORKLOAD_CLASSIFICATION: CLASSIFICATION_MODELS,
    WORKLOAD_DETECTION: DETECTION_MODELS,
    WORKLOAD_ENHANCEMENT: ENHANCEMENT_MODELS,
    WORKLOAD_GENAI: GENAI_MODELS,
    WORKLOAD_STRESS: CLASSIFICATION_MODELS,
}


def benchmark_form(
    key: str = "bench_form",
) -> Tuple[Optional[BenchmarkConfig], Optional[str]]:
    """Render the benchmark configuration form and return (config, action) on submit."""
    profile = _get_cached_profile()

    with st.form(key):
        st.markdown("### ⚙️ Benchmark Configuration")

        workload_options = [
            WORKLOAD_CLASSIFICATION,
            WORKLOAD_DETECTION,
            WORKLOAD_ENHANCEMENT,
            WORKLOAD_GENAI,
            WORKLOAD_STRESS,
        ]
        default_wl = st.session_state.get("chat_workload", WORKLOAD_CLASSIFICATION)
        wl_idx = (
            workload_options.index(default_wl) if default_wl in workload_options else 0
        )

        workload = st.selectbox(
            "Workload Type",
            workload_options,
            index=wl_idx,
            format_func=lambda w: w.replace("_", " ").title(),
            key=f"{key}_workload",
        )

        # Get hardware recommendations
        rec = get_recommended_config(profile, workload)

        st.info(f"💡 **AI Recommendation:** {rec['reasoning']}", icon="🤖")

        model_keys = rec["models"]
        # Fallback if no models
        if not model_keys:
            models = _WORKLOAD_MODELS.get(workload, CLASSIFICATION_MODELS)
            model_keys = list(models.keys())

        default_model = rec["default_model"] or (model_keys[0] if model_keys else None)
        model_idx = (
            model_keys.index(default_model) if default_model in model_keys else 0
        )
        model_key = st.selectbox(
            "Model",
            model_keys,
            index=model_idx,
            key=f"{key}_model",
            help="Filtered to models compatible with recommended backend.",
        )

        backend_options = [BACKEND_OPENVINO, BACKEND_ONNX]
        # Use recommender by default, user can override manually (though it might fail)
        default_backend = st.session_state.get("chat_backend", rec["backend"])
        back_idx = (
            backend_options.index(default_backend)
            if default_backend in backend_options
            else backend_options.index(rec["backend"])
        )

        backend = st.selectbox(
            "Backend", backend_options, index=back_idx, key=f"{key}_backend"
        )

        device_options = [DEVICE_CPU, DEVICE_GPU]
        # Filter available devices: e.g. if Mac, only show CPU
        if profile.os_name == "Darwin" or not profile.gpu.available:
            device_options = [DEVICE_CPU]

        default_dev = st.session_state.get("chat_device", rec["device"])
        # ensure selected device is in options
        if default_dev not in device_options:
            default_dev = device_options[0]

        dev_idx = (
            device_options.index(default_dev) if default_dev in device_options else 0
        )

        device = st.selectbox(
            "Device", device_options, index=dev_idx, key=f"{key}_device"
        )

        col1, col2 = st.columns(2)
        with col1:
            iterations = st.number_input(
                "Iterations", 1, 1000, DEFAULT_ITERATIONS, key=f"{key}_iter"
            )
        with col2:
            warmup = st.number_input(
                "Warmup Runs", 0, 100, DEFAULT_WARMUP, key=f"{key}_warmup"
            )

        batch_size = st.number_input(
            "Batch Size", 1, 64, DEFAULT_BATCH_SIZE, key=f"{key}_batch"
        )

        duration = None
        stress_target = ""
        if workload == WORKLOAD_STRESS:
            duration = st.number_input(
                "Stress Duration (s)",
                10,
                600,
                STRESS_DURATION_SECONDS,
                key=f"{key}_dur",
            )
            stress_target = st.selectbox(
                "Stress Target",
                ALL_STRESS_TARGETS,
                format_func=lambda t: STRESS_TARGET_LABELS.get(t, t),
                key=f"{key}_stress_target",
            )

        notes = st.text_input("Notes (optional)", "", key=f"{key}_notes")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_submitted = st.form_submit_button("🚀  Run Benchmark", type="primary")
        with col_btn2:
            tune_submitted = st.form_submit_button("🪄  Auto-Tune Configuration")

    if run_submitted or tune_submitted:
        config = BenchmarkConfig(
            workload_type=workload,
            model_key=model_key,
            backend=backend,
            device=device,
            iterations=iterations,
            warmup_iterations=warmup,
            batch_size=batch_size,
            duration_seconds=duration,
            stress_target=stress_target,
            notes=notes,
        )
        action = "run" if run_submitted else "autotune"
        return config, action

    return None, None
