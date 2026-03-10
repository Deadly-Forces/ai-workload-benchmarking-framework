"""System Info page — detailed hardware / software profile."""
from __future__ import annotations

import platform

import streamlit as st

from app.dashboard.components.layout import page_header, section_divider
from app.dashboard.components.metric_cards import metric_row
from app.features.system_profile.profiler import build_system_profile


def render_system_info() -> None:
    """Render the System Info page."""
    page_header("System Information", "Detailed hardware and software profile")

    profile = build_system_profile()

    # ── CPU ────────────────────────────────────────────────────────
    section_divider("CPU")
    if profile.cpu:
        metric_row([
            {"label": "Model", "value": profile.cpu.name[:35], "icon": "🖥️"},
            {"label": "Physical Cores", "value": str(profile.cpu.cores_physical), "icon": "⚙️"},
            {"label": "Logical Cores", "value": str(profile.cpu.cores_logical), "icon": "🔀"},
            {"label": "Base Freq", "value": f"{profile.cpu.frequency_mhz:.0f} MHz", "icon": "📶"},
        ])
    else:
        st.warning("CPU info unavailable")

    # ── Memory ────────────────────────────────────────────────────
    section_divider("Memory")
    if profile.memory:
        metric_row([
            {"label": "Total RAM", "value": f"{profile.memory.total_gb:.1f} GB", "icon": "💾"},
            {"label": "Available", "value": f"{profile.memory.available_gb:.1f} GB", "icon": "📦"},
            {"label": "Used %", "value": f"{profile.memory.percent_used:.1f}%", "icon": "📊"},
        ])
    else:
        st.warning("Memory info unavailable")

    # ── GPU ─────────────────────────────────────────────────────
    section_divider("GPU")
    if profile.gpu and profile.gpu.available:
        with st.expander(f"🎮  {profile.gpu.name}", expanded=True):
            cols = st.columns(3)
            cols[0].metric("VRAM", f"{profile.gpu.memory_mb:.0f} MB" if profile.gpu.memory_mb else "N/A")
            cols[1].metric("Driver", profile.gpu.driver_version or "N/A")
            cols[2].metric("Vendor", profile.gpu.vendor or "unknown")
    else:
        st.info("No discrete / identifiable GPU detected.")

    # ── Inference devices ─────────────────────────────────────────
    section_divider("Inference Backend Devices")
    if profile.inference_devices:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**OpenVINO**")
            for d in (profile.inference_devices.openvino_devices or []):
                st.code(d)
        with col2:
            st.markdown("**ONNX Runtime**")
            for p in (profile.inference_devices.onnx_providers or []):
                st.code(p)
    else:
        st.warning("No inference backends detected.")

    # ── OS / Python ───────────────────────────────────────────────
    section_divider("Software Environment")
    st.markdown(f"- **OS:** {platform.platform()}")
    st.markdown(f"- **Python:** {platform.python_version()}")
