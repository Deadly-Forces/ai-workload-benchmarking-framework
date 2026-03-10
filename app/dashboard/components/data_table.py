"""Data table component — styled dataframe rendering."""
from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from app.core.schemas import BenchmarkResult
from app.features.analysis.comparator import build_comparison


def render_results_table(results: List[BenchmarkResult]) -> None:
    """Show comparison table for a batch of results."""
    if not results:
        st.info("No results to display.")
        return

    entries = build_comparison(results)
    rows = []
    for e in entries:
        rows.append({
            "Model": e.model_name,
            "Backend": e.backend,
            "Device": e.device,
            "Mean Latency (ms)": round(e.mean_latency_ms, 2),
            "P95 Latency (ms)": round(e.p95_latency_ms, 2),
            "Throughput (FPS)": round(e.throughput_fps, 1),
            "CPU %": round(e.cpu_mean_pct, 1),
            "Mem Peak (MB)": round(e.memory_peak_mb, 1),
            "Score": round(e.score, 1),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=100, format="%.1f",
            ),
        },
    )


def render_single_result_detail(result: BenchmarkResult) -> None:
    """Show detail breakdown for one result."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mean Latency", f"{result.latency.avg_ms:.2f} ms" if result.latency else "N/A")
        st.metric("P95 Latency", f"{result.latency.p95_ms:.2f} ms" if result.latency else "N/A")
    with col2:
        st.metric("Throughput", f"{result.throughput_fps:.1f} FPS")
        st.metric("Iterations", result.iterations)
    with col3:
        cpu = result.resource_usage.avg_cpu_percent if result.resource_usage else 0
        mem = result.resource_usage.max_memory_mb if result.resource_usage else 0
        st.metric("CPU Mean", f"{cpu:.1f}%")
        st.metric("Memory Peak", f"{mem:.1f} MB")
