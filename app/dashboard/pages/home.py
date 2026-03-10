"""Home page — project overview, system quick-glance, recent runs."""
from __future__ import annotations

import streamlit as st

from app.config.constants import APP_NAME, APP_VERSION
from app.dashboard.components.layout import page_header, section_divider
from app.dashboard.components.metric_cards import metric_row
from app.features.system_profile.profiler import build_system_profile


def render_home() -> None:
    """Render the Home / Overview page."""
    page_header(
        APP_NAME,
        f"v{APP_VERSION}  •  AI Workload Benchmarking for Integrated & Mid-Range GPUs",
    )

    # Quick system summary
    profile = build_system_profile()
    section_divider("System Overview")

    metrics = [
        {"label": "CPU", "value": profile.cpu.name[:30] if profile.cpu else "N/A", "icon": "🖥️"},
        {"label": "Cores", "value": str(profile.cpu.cores_physical) if profile.cpu else "?", "icon": "⚙️"},
        {"label": "RAM", "value": f"{profile.memory.total_gb:.1f} GB" if profile.memory else "?", "icon": "💾"},
        {"label": "GPU", "value": (profile.gpu.name[:25] if profile.gpu and profile.gpu.available else "None"), "icon": "🎮"},
    ]
    metric_row(metrics)

    # Inference devices
    section_divider("Available Inference Devices")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**OpenVINO Devices**")
        if profile.inference_devices and profile.inference_devices.openvino_devices:
            for d in profile.inference_devices.openvino_devices:
                st.markdown(f"- `{d}`")
        else:
            st.caption("OpenVINO not available")
    with col2:
        st.markdown("**ONNX Runtime Providers**")
        if profile.inference_devices and profile.inference_devices.onnx_providers:
            for p in profile.inference_devices.onnx_providers:
                st.markdown(f"- `{p}`")
        else:
            st.caption("ONNX Runtime not available")

    # Suitability
    section_divider("Suitability Assessment")
    if profile.suitability:
        for key, val in profile.suitability.items():
            rating = val.get("rating", "")
            msg = f"**{key.upper()}:** {rating} — {val.get('note', '')}"
            if rating in ("Good", "Excellent", "Available", "Supported"):
                st.success(msg)
            elif rating in ("Recommended", "Limited"):
                st.warning(msg)
            elif rating in ("Not Installed", "CPU Only", "Not Available"):
                st.info(msg)
            else:
                st.info(msg)
    else:
        st.success("System looks ready for benchmarking!")

    # How to use
    section_divider("Quick Start")
    st.markdown(
        """
        1. Navigate to **Run Benchmark** in the sidebar.
        2. Select a workload type, model, backend, and device.
        3. Configure iterations and warmup, then click **Run**.
        4. View results on the **Results** page.
        5. Export reports as JSON or CSV from the Results page.
        """
    )
