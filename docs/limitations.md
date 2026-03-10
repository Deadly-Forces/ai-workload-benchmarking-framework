# Known Limitations

## Hardware Scope

- Designed and tested for **Intel Iris Xe** integrated graphics and
  comparable mid-range GPUs (Intel Arc A-series, AMD Radeon 680M).
- Not optimised for NVIDIA CUDA — the framework intentionally avoids CUDA
  dependencies.
- Discrete GPU memory monitoring relies on `GPUtil`, which may return
  incomplete data for integrated GPUs.

## Model Coverage

- Only three lightweight models are supported in the MVP:
  - **MobileNet-V2** (classification)
  - **YOLOv8n** (detection)
  - **ESPCN-x2** (super-resolution)
- Custom model loading is possible by subclassing `BaseBenchmarkRunner`
  but is not exposed in the dashboard UI.

## Inference Backends

- **OpenVINO** is the primary backend; if unavailable, the framework falls
  back to **ONNX Runtime** (CPU by default).
- DirectML acceleration via ONNX Runtime is supported but has not been
  extensively validated.
- No TensorRT, CUDA, or ROCm support.

## Monitoring Accuracy

- CPU / memory metrics are sampled at fixed 0.5 s intervals and may miss
  very short spikes.
- GPU utilisation on Intel integrated GPUs may report as 0% if the driver
  does not expose utilisation counters.
- Thermal readings depend on platform-specific sensor availability; they
  may be `None` on some systems.
- Disk stress testing skips partitions where the process lacks write
  permissions (e.g., recovery partitions).
- Network stress exercises the local network stack only; it does not
  generate external traffic or measure real throughput.

## Benchmark Validity

- Results are **relative**, not absolute — they are meaningful for
  comparing runs on the same machine under similar conditions.
- Background workloads (OS updates, antivirus scans, other applications)
  can significantly affect results.
- The composite score normalisation uses hardcoded reference values tuned
  for integrated GPUs; scores may be misleading on high-end discrete GPUs.

## UI / Dashboard

- The Streamlit dashboard stores results in `st.session_state`, which is
  lost when the browser tab is refreshed.  Results are also persisted to
  `storage/runs/` as JSON files, which survive restarts.
- Charts are rendered with Plotly — browser extensions that block
  JavaScript may prevent charts from appearing.

## Platform

- Developed and tested on **Windows 11**. Linux and macOS are expected to
  work but are not actively tested.
- Path handling uses `pathlib.Path`, which is cross-platform, but some
  external tools (e.g., `omz_downloader`) may behave differently on
  non-Windows systems.
