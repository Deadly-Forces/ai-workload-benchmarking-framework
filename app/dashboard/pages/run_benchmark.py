"""Run Benchmark page — form + live execution."""

from __future__ import annotations

import streamlit as st

from app.config.constants import (
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_STRESS,
    WORKLOAD_GENAI,
)
from app.config.logging_config import get_logger
from app.dashboard.components.layout import page_header, section_divider
from app.dashboard.components.benchmark_form import benchmark_form
from app.dashboard.components.status_panel import (
    render_status_panel,
    render_error_panel,
)
from app.dashboard.components.metric_cards import metric_row
from app.dashboard.components.charts import (
    render_latency_histogram,
    render_latency_timeline,
)
from app.features.benchmark_runner.schemas import BenchmarkConfig, RunProgress
from app.features.classification.benchmark import ClassificationBenchmark
from app.features.detection.benchmark import DetectionBenchmark
from app.features.enhancement.benchmark import EnhancementBenchmark
from app.features.genai.benchmark import GenAIBenchmark
from app.features.stress_test.benchmark import StressTestBenchmark
from app.features.autotune import optimize_batch_size, find_optimal_thread_count
from app.features.chat.intent_parser import get_intent_parser

logger = get_logger(__name__)

_RUNNERS = {
    WORKLOAD_CLASSIFICATION: ClassificationBenchmark,
    WORKLOAD_DETECTION: DetectionBenchmark,
    WORKLOAD_ENHANCEMENT: EnhancementBenchmark,
    WORKLOAD_GENAI: GenAIBenchmark,
    WORKLOAD_STRESS: StressTestBenchmark,
}


def _run_benchmark(config: BenchmarkConfig):
    """Execute the benchmark and populate session state."""
    runner_cls = _RUNNERS.get(config.workload_type)
    if runner_cls is None:
        st.error(f"Unsupported workload: {config.workload_type}")
        return

    progress_placeholder = st.empty()
    progress = RunProgress()

    def _on_progress(p: RunProgress):
        nonlocal progress
        progress = p
        with progress_placeholder.container():
            render_status_panel(p)

    try:
        runner = runner_cls(config)
        result = runner.run(progress_callback=_on_progress)
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"Benchmark failed: {e}")
        logger.exception("Benchmark error")
        return

    # Store result
    if "results" not in st.session_state:
        st.session_state["results"] = []
    st.session_state["results"].append(result)
    st.session_state["last_result"] = result

    # Show quick summary
    section_divider("Results Summary")
    metric_row(
        [
            {
                "label": "Mean Latency",
                "value": f"{result.latency.avg_ms:.2f} ms",
                "icon": "⏱️",
            },
            {
                "label": "P95 Latency",
                "value": f"{result.latency.p95_ms:.2f} ms",
                "icon": "📊",
            },
            {
                "label": "Throughput",
                "value": f"{result.throughput_fps:.1f} FPS",
                "icon": "⚡",
            },
            {"label": "Iterations", "value": str(result.iterations), "icon": "🔄"},
        ]
    )

    section_divider("Latency Analysis")
    col1, col2 = st.columns(2)
    with col1:
        render_latency_histogram(result.latency)
    with col2:
        render_latency_timeline(result.latency)

    if result.errors:
        render_error_panel(result.errors)


def render_run_benchmark() -> None:
    """Render the Run Benchmark page."""
    page_header("Run Benchmark", "Configure and execute an AI workload benchmark")

    st.markdown("### 💬 Ask AI to Benchmark")
    chat_intent = st.chat_input(
        "E.g., 'Run a stress test on GPU' or 'Test generative AI on CPU'"
    )
    if chat_intent:
        with st.spinner("🤖 Parsing intent with zero-shot NLP..."):
            parser = get_intent_parser()
            parsed_config = parser.parse_user_intent(chat_intent)

            st.session_state["chat_workload"] = parsed_config.get("workload_type")
            st.session_state["chat_device"] = parsed_config.get("device")
            st.session_state["chat_backend"] = parsed_config.get("backend")

            st.success(
                "Parsed workload: "
                f"{str(parsed_config.get('workload_type')).replace('_', ' ').title()}, "
                f"Device: {parsed_config.get('device')}"
            )
            st.rerun()

    st.markdown("---")

    config, action = benchmark_form()
    if config is not None:
        if action == "run":
            _run_benchmark(config)
        elif action == "autotune":
            st.info("🪄 Running Auto-Tune configuration...")

            with st.spinner("Optimizing Batch Size..."):
                batch_res = optimize_batch_size(config)

            with st.spinner("Optimizing Thread Count..."):
                thread_res = find_optimal_thread_count(config)

            st.success("Auto-Tuning Complete!")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Optimal Batch Size", batch_res["optimal_batch_size"])
                st.write(f"Best FPS: {batch_res['best_throughput']:.1f}")
            with col2:
                st.metric("Optimal Threads", thread_res["optimal_num_threads"])
                st.write(f"Best FPS: {thread_res['best_throughput']:.1f}")

            with st.expander("View Auto-Tune History"):
                st.write("**Batch History:**", batch_res["history"])
                st.write("**Thread History:**", thread_res["history"])
