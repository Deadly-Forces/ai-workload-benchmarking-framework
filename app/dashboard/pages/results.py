"""Results page — history browser, comparisons, exports."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.config.settings import EXPORTS_DIR
from app.dashboard.components.layout import page_header, section_divider
from app.dashboard.components.metric_cards import metric_row
from app.dashboard.components.charts import (
    render_latency_histogram,
    render_latency_timeline,
    render_throughput_comparison,
    render_resource_chart,
    render_score_radar,
)
from app.dashboard.components.data_table import (
    render_results_table,
    render_single_result_detail,
)
from app.features.analysis.scoring import compute_score
from app.features.analysis.ai_reporter import generate_insight_report
from app.features.reporting.report_builder import build_report
from app.core.schemas import BenchmarkResult


def render_results() -> None:
    """Render the Results / History page."""
    page_header("Results", "Browse, compare, and export benchmark results")

    results: list[BenchmarkResult] = st.session_state.get("results", [])

    if not results:
        st.info("No results yet.  Go to **Run Benchmark** to generate data.")
        return

    # ── Overview table ────────────────────────────────────────────
    section_divider("All Results")
    render_results_table(results)

    # ── Detail view for selected result ───────────────────────────
    section_divider("Result Detail")
    labels = [
        f"#{i+1}  {r.model_name} ({r.backend}/{r.device})"
        for i, r in enumerate(results)
    ]
    selected_idx = st.selectbox(
        "Select a result", range(len(labels)), format_func=lambda i: labels[i]
    )
    result = results[selected_idx]

    render_single_result_detail(result)

    col1, col2 = st.columns(2)
    with col1:
        if result.latency:
            render_latency_histogram(result.latency)
    with col2:
        if result.latency:
            render_latency_timeline(result.latency)

    # Score radar
    score = compute_score(result)
    render_score_radar(
        {
            "Latency": score.latency_score,
            "Throughput": score.throughput_score,
            "Resource": score.resource_score,
            "Stability": score.stability_score,
        }
    )

    # AI Insights
    section_divider("🤖 AI Performance Insights")
    if st.button("Generate AI Insight Report", key=f"ai_report_btn_{result.run_id}"):
        with st.spinner("Analyzing metrics with local LLM..."):
            insight = generate_insight_report(result)
            st.info(insight, icon="🧠")

    # ── Multi-result comparison ───────────────────────────────────
    if len(results) > 1:
        section_divider("Comparison")
        render_throughput_comparison(results)

    # ── Export ─────────────────────────────────────────────────────
    section_divider("Export")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        if st.button("📄  Export JSON"):
            paths = build_report(results, formats=["json"])
            st.success(f"Exported → {paths.get('json')}")
    with exp_col2:
        if st.button("📊  Export CSV"):
            paths = build_report(results, formats=["csv"])
            st.success(f"Exported → {paths.get('csv')}")
