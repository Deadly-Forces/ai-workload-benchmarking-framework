# Architecture

## Overview

The AI Workload Benchmarking Framework follows a **feature-based modular architecture**
with clear separation between backend logic and the Streamlit dashboard UI.

```text
ai-workload-benchmarking-framework/
├── app/
│   ├── config/          # Settings, constants, theme, logging
│   ├── core/            # Shared exceptions, utilities, schemas, timer
│   ├── features/        # Backend feature modules
│   │   ├── system_profile/   # Hardware & OS detection
│   │   ├── monitoring/       # Real-time resource sampling
│   │   ├── benchmark_runner/ # Abstract runner + orchestrator
│   │   ├── classification/   # MobileNet-V2 image classification
│   │   ├── detection/        # YOLOv8n object detection
│   │   ├── enhancement/      # ESPCN-x2 super-resolution
│   │   ├── stress_test/      # Sustained load & component stress testing
│   │   │   ├── benchmark.py       # Standard benchmark adapter
│   │   │   ├── runner.py          # Core stress test execution
│   │   │   ├── stress_generators.py  # CPU/GPU/Memory/Disk/Network stress workers
│   │   │   ├── degradation_analysis.py  # Latency drift detection
│   │   │   └── schemas.py         # Stress test data structures
│   │   ├── reliability/      # Output consistency checking
│   │   ├── analysis/         # Aggregation, scoring, comparison
│   │   └── reporting/        # JSON / CSV export, chart building
│   ├── dashboard/       # Streamlit UI layer
│   │   ├── styles/      # CSS (base, theme, animations)
│   │   ├── components/  # Reusable UI widgets
│   │   └── pages/       # Full page views
│   └── main.py          # Streamlit entry point
├── scripts/             # CLI utilities
├── models/              # Downloaded model files
├── datasets/            # Test images
├── storage/             # Benchmark results & exports
├── docs/                # This documentation
└── tests/               # Unit & integration tests
```

## Layer Responsibilities

### Config Layer (`app/config/`)

- **settings.py** — Paths derived from environment variables + defaults.
- **constants.py** — Model registries, scoring weights, monitoring intervals.
- **theme.py** — Dataclass-based design tokens (colors, fonts, spacing, shadows).
- **logging_config.py** — Structured logging with rotation.

### Core Layer (`app/core/`)

Shared types and utilities consumed by every feature:

- `BenchmarkResult` — canonical result dataclass.
- `PrecisionTimer` / `LatencyCollector` — nanosecond-resolution timing.
- `BenchmarkError` hierarchy — typed exception tree.

### Feature Layer (`app/features/`)

Each feature is a self-contained package exposing a public API through its
`__init__.py`. Features depend on **core** and **config**, never on each other
(with the exception of the analysis/reporting features which read
`BenchmarkResult` instances produced by workload features).

### Dashboard Layer (`app/dashboard/`)

Pure presentation — calls into feature modules and renders results with
Streamlit. The `state.py` module manages `st.session_state` to keep results
across page navigations.

## Inference Backend Strategy

```text
                 ┌──────────────┐
                 │  Model Loader │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              │                   │
       ┌──────▼──────┐    ┌──────▼──────┐
       │  OpenVINO   │    │ ONNX Runtime│
       │  (primary)  │    │ (fallback)  │
       └─────────────┘    └─────────────┘
```

- **OpenVINO** is preferred for Intel integrated GPUs (Iris Xe).
- **ONNX Runtime** is the universal fallback (CPU / DirectML).
- Both are imported conditionally via `try/except` so the framework
  gracefully degrades when either is absent.

## Data Flow

1. User configures a benchmark via the dashboard form or CLI script.
2. `BenchmarkOrchestrator` warms up the model, then delegates to the
   workload-specific `BaseBenchmarkRunner` subclass.
3. `ResourceSampler` collects CPU / memory / GPU / thermal metrics in a
   background thread during the run.
4. Latency measurements are collected per-iteration by `LatencyCollector`.
5. Results are packaged into `BenchmarkResult` dataclasses.
6. The analysis module scores and (optionally) compares results.
7. The reporting module exports JSON / CSV and builds Plotly charts.
8. The dashboard renders charts, metric cards, and tables.

## Scoring Model

Composite score (0-100) comprises four normalised dimensions:

| Dimension   | Weight | Source                          |
|-------------|--------|---------------------------------|
| Latency     | 30%    | Median latency (lower is better)|
| Throughput  | 30%    | FPS (higher is better)          |
| Resource    | 20%    | Peak CPU + memory (lower better)|
| Stability   | 20%    | Latency CV (lower is better)    |

See [benchmark-methodology.md](benchmark-methodology.md) for details.
