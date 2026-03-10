# Setup Guide

## Prerequisites

| Requirement | Version | Notes                                 |
|-------------|---------|---------------------------------------|
| Python      | ≥ 3.10  | 3.11 recommended                      |
| pip         | latest  | `python -m pip install --upgrade pip` |
| Git         | any     | For cloning the repository            |

## Installation

```bash
# 1 — Clone the repository
git clone <repo-url> ai-workload-benchmarking-framework
cd ai-workload-benchmarking-framework

# 2 — Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3 — Install dependencies
pip install -r requirements.txt
```

## Environment Variables (optional)

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable                 | Default            | Description               |
|--------------------------|--------------------|---------------------------|
| `BENCHMARK_LOG_LEVEL`    | `INFO`             | Logging verbosity         |
| `BENCHMARK_STORAGE_DIR`  | `<project>/storage`| Where results are saved   |
| `BENCHMARK_MODELS_DIR`   | `<project>/models` | Where models are stored   |

## Download Models

Fetch pre-trained ONNX models (MobileNet-V2, YOLOv8n, ESPCN):

```bash
python scripts/download_models.py --all
```

Or download individual model families:

```bash
python scripts/download_models.py --classification
python scripts/download_models.py --detection
python scripts/download_models.py --enhancement
```

> **Note:** The detection model (YOLOv8n) requires the `ultralytics` package
> to export from PyTorch to ONNX. Install it with `pip install ultralytics`.

## Prepare Datasets

Generate synthetic test images for quick verification:

```bash
python scripts/prepare_datasets.py
```

This creates 20 random PNG images in `datasets/synthetic/`.

## Running the Dashboard

```bash
streamlit run app/main.py
```

The dashboard opens at `http://localhost:8501`.

## Running from the CLI

Run a single classification benchmark without the dashboard:

```bash
python scripts/run_sample_benchmark.py
```

Export stored results to a report:

```bash
python scripts/export_report.py --format json
python scripts/export_report.py --format csv
```

## Troubleshooting

| Problem                            | Solution                                                  |
|------------------------------------|-----------------------------------------------------------|
| `ModuleNotFoundError: openvino`    | `pip install openvino` or accept ONNX Runtime fallback    |
| `ModuleNotFoundError: onnxruntime` | `pip install onnxruntime`                                 |
| GPU not detected                   | Ensure Intel GPU drivers are up to date                   |
| Streamlit port conflict            | `streamlit run app/main.py --server.port 8502`            |
| No models found                    | Re-run `scripts/download_models.py --all`                 |
