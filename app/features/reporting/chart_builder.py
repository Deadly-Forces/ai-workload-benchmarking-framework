"""Chart builder — generate Plotly figures for the dashboard and reports."""
from __future__ import annotations

from typing import Dict, List, Optional

import plotly.graph_objects as go

from app.config.theme import COLORS
from app.core.schemas import BenchmarkResult, LatencyStats


# ── shared layout ────────────────────────────────────────────────────
_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,14,26,0.6)",
    font=dict(family="Inter, sans-serif", color=COLORS.text_primary),
    margin=dict(l=50, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _apply_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**_BASE_LAYOUT, title_text=title)  # type: ignore[arg-type]
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
    return fig


# ── latency distribution ─────────────────────────────────────────────
def latency_histogram(stats: LatencyStats, title: str = "Latency Distribution") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=stats.all_latencies_ms,
        nbinsx=40,
        marker_color=COLORS.primary_blue,
        opacity=0.85,
        name="Latency",
    ))
    fig.add_vline(x=stats.avg_ms, line_dash="dash", line_color=COLORS.cyan_accent,
                  annotation_text=f"Mean {stats.avg_ms:.2f} ms")
    fig.add_vline(x=stats.p95_ms, line_dash="dot", line_color=COLORS.warning,
                  annotation_text=f"P95 {stats.p95_ms:.2f} ms")
    return _apply_layout(fig, title)


# ── latency over iterations ──────────────────────────────────────────
def latency_timeline(stats: LatencyStats, title: str = "Latency Over Iterations") -> go.Figure:
    fig = go.Figure()
    x = list(range(1, len(stats.all_latencies_ms) + 1))
    fig.add_trace(go.Scatter(
        x=x, y=stats.all_latencies_ms,
        mode="lines", line=dict(color=COLORS.primary_blue, width=1.5),
        name="Latency",
    ))
    fig.add_hline(y=stats.avg_ms, line_dash="dash", line_color=COLORS.cyan_accent)
    fig.update_xaxes(title_text="Iteration")
    fig.update_yaxes(title_text="Latency (ms)")
    return _apply_layout(fig, title)


# ── throughput comparison bar ─────────────────────────────────────────
def throughput_bar(results: List[BenchmarkResult], title: str = "Throughput Comparison") -> go.Figure:
    labels = [f"{r.model_name}\n{r.backend}" for r in results]
    values = [r.throughput_fps for r in results]
    colors = [COLORS.primary_blue if i % 2 == 0 else COLORS.cyan_accent for i in range(len(results))]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors))
    fig.update_yaxes(title_text="FPS")
    return _apply_layout(fig, title)


# ── resource usage area chart ─────────────────────────────────────────
def resource_area(
    cpu_samples: List[float],
    mem_samples: List[float],
    title: str = "Resource Usage",
) -> go.Figure:
    fig = go.Figure()
    x = list(range(len(cpu_samples)))
    fig.add_trace(go.Scatter(
        x=x, y=cpu_samples, fill="tozeroy",
        line=dict(color=COLORS.primary_blue), name="CPU %",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=mem_samples, fill="tozeroy",
        line=dict(color=COLORS.cyan_accent), name="Mem MB",
        yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="CPU %"),
        yaxis2=dict(title="Memory (MB)", overlaying="y", side="right"),
    )
    return _apply_layout(fig, title)


# ── radar / spider chart for scoring ─────────────────────────────────
def score_radar(breakdown: Dict[str, float], title: str = "Score Breakdown") -> go.Figure:
    cats = list(breakdown.keys())
    vals = list(breakdown.values())
    cats.append(cats[0])
    vals.append(vals[0])
    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself",
                                     line_color=COLORS.cyan_accent))
    fig.update_layout(polar=dict(
        bgcolor="rgba(10,14,26,0.6)",
        radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
        angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    ))
    return _apply_layout(fig, title)
