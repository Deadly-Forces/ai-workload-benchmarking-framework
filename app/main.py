"""
AI Workload Benchmarking Framework — Streamlit Entry Point
===========================================================
Run with:  streamlit run app/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path so absolute imports work.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from app.config.constants import APP_NAME
from app.config.logging_config import setup_logging
from app.dashboard.components.layout import inject_css
from app.dashboard.state import init_state
from app.dashboard.pages.home import render_home
from app.dashboard.pages.run_benchmark import render_run_benchmark
from app.dashboard.pages.results import render_results
from app.dashboard.pages.system_info import render_system_info
from app.dashboard.pages.methodology import render_methodology

# ── Streamlit page config ───────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap ───────────────────────────────────────────────────────
setup_logging()
init_state()
inject_css()

# ── Navigation ──────────────────────────────────────────────────────
_PAGES = {
    "🏠  Home": render_home,
    "🚀  Run Benchmark": render_run_benchmark,
    "📊  Results": render_results,
    "🖥️  System Info": render_system_info,
    "📖  Methodology": render_methodology,
}

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center;padding:1rem 0 1.5rem;">
            <h2 style="
                font-family:'Orbitron',sans-serif;
                font-size:1.1rem;
                background:linear-gradient(135deg,#00D4FF,#0D6EFD);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
            ">⚡ {APP_NAME}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selection = st.radio("Navigation", list(_PAGES.keys()), label_visibility="collapsed")

    st.markdown("---")
    result_count = len(st.session_state.get("results", []))
    st.caption(f"📦 {result_count} result(s) in session")

    if st.button("🗑️  Clear Session", width="stretch"):
        from app.dashboard.state import clear_results
        clear_results()
        st.rerun()

# ── Render selected page ────────────────────────────────────────────
page_fn = _PAGES[selection]
page_fn()
