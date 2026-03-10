"""Charts component — wraps Plotly chart rendering with consistent styling."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from app.core.schemas import BenchmarkResult, LatencyStats
from app.features.reporting.chart_builder import (
    latency_histogram,
    latency_timeline,
    throughput_bar,
    resource_area,
    score_radar,
)


def render_latency_histogram(stats: LatencyStats, *, title: str = "Latency Distribution") -> None:
    fig = latency_histogram(stats, title=title)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_latency_timeline(stats: LatencyStats, *, title: str = "Latency Over Iterations") -> None:
    fig = latency_timeline(stats, title=title)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_throughput_comparison(results: list[BenchmarkResult], *, title: str = "Throughput Comparison") -> None:
    fig = throughput_bar(results, title=title)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_resource_chart(
    cpu_samples: list[float],
    mem_samples: list[float],
    *,
    title: str = "Resource Usage",
) -> None:
    fig = resource_area(cpu_samples, mem_samples, title=title)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_score_radar(breakdown: dict[str, float], *, title: str = "Score Breakdown") -> None:
    fig = score_radar(breakdown, title=title)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
