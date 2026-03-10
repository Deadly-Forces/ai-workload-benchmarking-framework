"""Metric cards — glowing KPI tiles for the dashboard."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from app.config.theme import COLORS


def metric_card(
    label: str,
    value: str,
    *,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    icon: str = "",
) -> None:
    """Render a single cyber-styled metric card."""
    delta_html = ""
    if delta:
        cls = "positive" if delta_positive else "negative"
        arrow = "&#9650;" if delta_positive else "&#9660;"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'

    icon_html = f'<span style="font-size:1.3rem;margin-right:0.4rem;">{icon}</span>' if icon else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{icon_html}{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards using st.columns."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            metric_card(**m)
