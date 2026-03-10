# AI Workload Benchmarking Framework for Integrated and Mid-Range Graphics Systems

A modular Python application that benchmarks lightweight AI workloads on consumer hardware, with special focus on Intel integrated GPUs (Intel Iris Xe). It includes a Streamlit dashboard for real-time monitoring, AI-assisted analysis, and GenAI LLM benchmarking across CPU and GPU-capable OpenVINO devices.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![OpenVINO](https://img.shields.io/badge/OpenVINO-2023.3+-purple)
![OpenVINO GenAI](https://img.shields.io/badge/OpenVINO_GenAI-2024.0+-blueviolet)

---

## Features

### Core Benchmarking
- **AI Inference Benchmarking** — Run lightweight models (MobileNetV2, YOLOv8n, ESPCN) on CPU and GPU
- **GenAI LLM Benchmarking** — Benchmark generative AI models (TinyLlama 1.1B) with TTFT and Tokens-Per-Second metrics
- **CPU vs GPU Comparison** — Compare latency, throughput, and resource usage across devices
- **System Profiling** — Detect CPU, GPU, RAM, available inference devices
- **Live Monitoring** — Track CPU/memory/thermal metrics during execution
- **Sustained Performance Analysis** — Detect latency drift over extended runs
- **Component Stress Testing** — Stress individual or combined hardware: CPU, GPU, Memory, Disk (all partitions), Network, CPU+GPU, or All at once
- **Reliability Testing** — Measure output consistency across repeated inferences
- **Export & Reporting** — Save results as JSON/CSV, generate visual charts

### AI-Powered Features
- **AI Insight Reports** — Automatically generate human-readable performance analysis using a local TinyLlama model that interprets benchmark metrics, identifies bottlenecks, and provides recommendations
- **Chat-Driven Benchmarking** — Describe benchmarks in natural language (e.g., *"Run a classification test on GPU"*); a DistilBERT zero-shot classifier parses your intent into a structured benchmark configuration
- **AI Auto-Tuning** — Automatically find optimal batch sizes and thread counts by running iterative micro-benchmarks and selecting the configuration with the highest throughput
- **Dynamic Model Selection** — The framework detects your system specs (CPU, GPU, RAM) and automatically selects the best model and backend; models are downloaded from HuggingFace on-demand if not found locally

### Dashboard
- **Futuristic Dashboard** — Blue-black cyber-tech themed Streamlit UI with smooth animations and interactive charts

## Target Hardware

- Intel Core i5-class CPU
- Intel Iris Xe integrated GPU
- Consumer laptop environment
- No CUDA dependency — works with Intel GPU via OpenVINO
- Gracefully degrades when GPU is unavailable

## Quick Start

### 1. Clone and Install

```bash
git lfs install
git clone https://github.com/Deadly-Forces/ai-workload-benchmarking-framework.git
cd ai-workload-benchmarking-framework
git lfs pull
pip install -r requirements.txt
```

> **Important:** The repository uses Git LFS for the large TinyLlama OpenVINO model binary. If `git lfs pull` is skipped, GenAI benchmarks will fail until the LFS objects are downloaded.

### 2. Models and Assets

```bash
# Refresh or re-download inference models (MobileNetV2, YOLOv8n, ESPCN)
python scripts/download_models.py

# Re-download the GenAI model from Hugging Face if needed
python scripts/download_genai_models.py
```

By default, the framework reads models from the repository-level `models/` directory, datasets from `datasets/`, and benchmark outputs from `storage/`. These locations can be overridden with:

- `BENCHMARK_MODELS_DIR`
- `BENCHMARK_DATASETS_DIR`
- `BENCHMARK_STORAGE_DIR`

The repository already includes the main TinyLlama OpenVINO binary through Git LFS. The download scripts are still useful if you want to refresh local assets or rebuild missing files.

> **Note:** Some models are also downloaded automatically on first use if not present locally.

### 3. Prepare Sample Datasets

```bash
python scripts/prepare_datasets.py
```

Creates sample test images in `datasets/`.

### 4. Run the Dashboard

```bash
streamlit run app/main.py
```

Open your browser at `http://localhost:8501`.

### 5. Run a Sample Benchmark (CLI)

```bash
python scripts/run_sample_benchmark.py
```

## Project Structure

```text
ai-workload-benchmarking-framework/
├── app/
│   ├── main.py                    # Streamlit entry point
│   ├── config/                    # Settings, constants, theme
│   ├── core/                      # Shared utilities, schemas, paths
│   ├── features/
│   │   ├── system_profile/        # Hardware detection
│   │   ├── benchmark_runner/      # Orchestration engine
│   │   ├── classification/        # Image classification benchmark
│   │   ├── detection/             # Object detection benchmark
│   │   ├── enhancement/           # Image enhancement benchmark
│   │   ├── genai/                 # GenAI LLM benchmarking
│   │   │   ├── benchmark.py       # LLM benchmark runner (TTFT, TPS)
│   │   │   ├── model_utils.py     # Model loading & HuggingFace download
│   │   │   └── schemas.py         # GenAI-specific metrics
│   │   ├── chat/                  # Chat-driven benchmarking
│   │   │   └── intent_parser.py   # NLP intent parsing (DistilBERT)
│   │   ├── autotune/              # AI auto-tuning
│   │   │   └── optimizer.py       # Batch size & thread optimization
│   │   ├── stress_test/           # Sustained load testing with component stress
│   │   │   ├── benchmark.py       # Standard benchmark adapter
│   │   │   ├── runner.py          # Core stress test runner
│   │   │   ├── stress_generators.py  # CPU/GPU/Memory/Disk/Network stress workers
│   │   │   ├── degradation_analysis.py  # Latency drift detection
│   │   │   └── schemas.py         # Stress test data structures
│   │   ├── reliability/           # Output consistency testing
│   │   ├── monitoring/            # CPU/GPU/memory/thermal sampling
│   │   ├── analysis/              # Statistics, scoring & AI reports
│   │   │   ├── ai_reporter.py     # AI-generated performance reports (TinyLlama)
│   │   │   ├── aggregations.py    # Metric aggregation
│   │   │   ├── comparator.py      # CPU vs GPU comparison
│   │   │   ├── scoring.py         # Performance scoring
│   │   │   └── statistics.py      # Statistical analysis
│   │   └── reporting/             # JSON/CSV export, charts
│   ├── dashboard/                 # Streamlit pages, components, styles
│   │   ├── styles/                # CSS (base, theme, animations)
│   │   ├── components/            # Reusable UI widgets
│   │   └── pages/                 # Full page views
│   ├── models/                    # Downloaded model files
│   ├── datasets/                  # Sample test images
│   └── storage/                   # Benchmark results and exports
├── models/                        # Pre-trained ONNX model files
├── datasets/                      # Test images
├── storage/                       # Persistent benchmark results & exports
├── scripts/                       # CLI utilities
├── tests/                         # Unit & integration tests
├── docs/                          # Documentation
├── requirements.txt
└── README.md
```

## Benchmark Workloads

| Workload | Model | Description |
| --- | --- | --- |
| Classification | MobileNetV2 | Image classification inference |
| Detection | YOLOv8n (ONNX) | Lightweight object detection |
| Enhancement | ESPCN x2 | Super-resolution upscaling |
| GenAI | TinyLlama 1.1B (INT4) | LLM text generation (TTFT & TPS) |
| Stress Test | Any above | Sustained load over duration |
| Reliability | Any above | Output consistency analysis |

### Stress Test Targets

When running a stress test, you can select which hardware component(s) to stress:

| Target | What is stressed |
| --- | --- |
| CPU | Heavy matrix math (dot products, SVD decompositions) |
| GPU | Large tensor multiplications |
| Memory | Repeated large allocations + hashing |
| Disk (All Partitions) | Sequential 4 MB write/read on every writable partition |
| Network (Wi-Fi/Ethernet) | Network stack exercise (DNS, TCP connects) |
| CPU + GPU | CPU and GPU combined |
| All Combined | CPU + GPU + Memory + Disk + Network simultaneously |

## Metrics Collected

- **Latency**: Average, min, max, P95
- **Throughput**: Inferences per second
- **GenAI Metrics**: Time-To-First-Token (TTFT), Tokens Per Second (TPS)
- **CPU Usage**: Per-sample CPU utilization
- **Memory Usage**: RSS and percent
- **GPU Usage**: Utilization and memory (when available)
- **Disk I/O**: Write/read throughput across partitions (stress tests)
- **Network I/O**: Network stack latency (stress tests)
- **Thermal**: Temperature readings (when available)
- **Consistency**: Output variance across identical runs
- **Speedup**: CPU vs GPU performance ratio
- **Degradation**: Latency drift under sustained load

## Tech Stack

- **Python 3.10+**
- **Streamlit** — Interactive dashboard
- **OpenVINO** — Primary inference backend (Intel GPU support)
- **OpenVINO GenAI** — LLM text generation pipeline
- **ONNX Runtime** — Fallback inference backend
- **HuggingFace Hub** — Model downloads & management
- **Transformers** — NLP intent parsing (DistilBERT zero-shot)
- **scikit-learn** — Machine learning utilities
- **Plotly** — Interactive charts
- **pandas / NumPy** — Data analysis
- **psutil** — System monitoring
- **OpenCV** — Image preprocessing

## Configuration

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
```

Key settings are in `app/config/settings.py`.

Useful path overrides:

```bash
BENCHMARK_MODELS_DIR=./models
BENCHMARK_DATASETS_DIR=./datasets
BENCHMARK_STORAGE_DIR=./storage
```

## Limitations

- Thermal monitoring requires platform-specific sensor access
- GPU monitoring is best-effort on integrated graphics
- Model accuracy is not the focus — this benchmarks inference speed
- Designed for lightweight models only
- GenAI models require ~1–2 GB disk space and sufficient RAM (~4 GB+)
- Cloning the repository requires Git LFS to fetch the large TinyLlama model binary
- Chat-driven intent parsing requires an internet connection on first use to download the DistilBERT model

## License

MIT License — see LICENSE for details.
