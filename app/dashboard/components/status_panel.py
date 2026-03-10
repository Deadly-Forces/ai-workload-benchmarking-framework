"""Status panel — real-time progress display during benchmark runs."""
from __future__ import annotations

import streamlit as st

from app.features.benchmark_runner.schemas import RunProgress


def render_status_panel(progress: RunProgress) -> None:
    """Show a live status panel for an in-progress benchmark."""
    phase_icons = {
        "idle": "⏸️",
        "loading": "📦",
        "warmup": "🔥",
        "running": "⚡",
        "complete": "✅",
        "error": "❌",
    }
    icon = phase_icons.get(progress.phase, "🔄")

    phase_class = "running"
    if progress.phase == "complete":
        phase_class = "success"
    elif progress.phase == "error":
        phase_class = "error"

    st.markdown(
        f"""
        <div class="glass-panel" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span class="status-badge {phase_class}">{icon} {progress.phase.upper()}</span>
                </div>
                <div style="color:#94A3B8;font-size:0.85rem;">{progress.message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if progress.total_iterations and progress.total_iterations > 0:
        pct = progress.current_iteration / progress.total_iterations
        st.progress(min(pct, 1.0))
        st.caption(
            f"Iteration {progress.current_iteration}/{progress.total_iterations}"
            f"  •  Last latency: {progress.last_latency_ms:.2f} ms"
            if progress.last_latency_ms else
            f"Iteration {progress.current_iteration}/{progress.total_iterations}"
        )


def render_error_panel(errors: list[str]) -> None:
    """Show collected errors."""
    if not errors:
        return
    with st.expander(f"⚠️ {len(errors)} error(s) during run", expanded=False):
        for e in errors:
            st.error(e)
