"""Methodology page — explains benchmark methodology and scoring."""
from __future__ import annotations

import streamlit as st

from app.dashboard.components.layout import page_header, section_divider


def render_methodology() -> None:
    """Render the Methodology / About page."""
    page_header("Methodology", "How benchmarks are run and scored")

    section_divider("Benchmark Protocol")
    st.markdown(
        """
        Each benchmark follows a strict protocol:

        1. **Model Loading** — The selected model is loaded via OpenVINO or ONNX Runtime.
           If the primary backend is unavailable, the framework falls back to CPU-only mode.

        2. **Input Preparation** — A synthetic input tensor matching the model's expected
           shape is generated.  For image workloads the input simulates a standard resolution
           (e.g., 224×224 for classification, 640×640 for detection).

        3. **Warmup Phase** — A configurable number of warmup iterations are executed and
           discarded to allow JIT compilation, memory allocation, and cache priming.

        4. **Timed Iterations** — Each iteration is timed using `time.perf_counter()` for
           sub-millisecond precision.  Resource samples (CPU %, memory, GPU if available,
           thermals) are collected in a background thread at 2 Hz.

        5. **Statistics** — Latency samples are aggregated into mean, median, standard
           deviation, min, max, and percentile (P95, P99) statistics.
        """
    )

    section_divider("Scoring Model")
    st.markdown(
        """
        Each benchmark result receives a **composite score (0–100)** computed from four
        equally important dimensions:

        | Dimension     | Weight | Description                                         |
        |---------------|--------|-----------------------------------------------------|
        | **Latency**   | 30%    | Lower mean latency → higher score                  |
        | **Throughput** | 30%    | Higher FPS → higher score                           |
        | **Resource**  | 20%    | Lower CPU usage → better resource efficiency        |
        | **Stability** | 20%    | Lower coefficient of variation → more consistent    |

        Normalisation maps each metric to [0, 1] using configurable reference ranges
        (e.g., max acceptable latency = 200 ms, max throughput ceiling = 100 FPS).
        """
    )

    section_divider("Stress Test")
    st.markdown(
        """
        The stress test runs inference continuously for a configurable duration
        (default 60 s).  Latency drift is assessed by comparing the mean latency
        of the **first quarter** vs. the **last quarter** of samples.  A drift
        greater than **10 %** flags potential thermal throttling or resource
        contention.
        """
    )

    section_divider("Reliability / Consistency Check")
    st.markdown(
        """
        The same input is fed through the model N times.  All outputs are compared
        byte-for-byte against the first (reference) output.  An absolute-difference
        tolerance (default 1e-5) accounts for floating-point non-determinism.
        Results report the number of identical runs vs. drifted runs and the
        maximum observed drift.
        """
    )

    section_divider("Limitations")
    st.markdown(
        """
        - Synthetic inputs may not reflect real-world inference cost accurately.
        - GPU monitoring on integrated GPUs is best-effort; some metrics may be
          unavailable.
        - Thermal readings require OS / driver support and may return 0 on some
          systems.
        - Batch sizes > 1 are supported but model-specific; not all models handle
          dynamic batching.
        """
    )
