# Benchmark Methodology

## Protocol

Each benchmark run follows a deterministic protocol:

1. **System Profiling** — Detect CPU, GPU, memory, OS, and available
   inference backends.
2. **Model Loading** — Load the workload model via OpenVINO (preferred)
   or ONNX Runtime (fallback).
3. **Warm-up Phase** — Execute `warmup_iterations` (default 5) inferences
   that are **excluded** from results to prime caches and JIT paths.
4. **Timed Iterations** — Run `iterations` (default 100) inferences while
   collecting per-iteration latency with nanosecond precision.
5. **Resource Monitoring** — A background thread samples CPU %, memory %,
   GPU utilisation, and thermal data at 0.5 s intervals throughout the run.
6. **Result Aggregation** — Compute latency percentiles, throughput (FPS),
   peak/mean resource utilisation, thermal envelope, and a composite score.

## Workloads

### Image Classification (MobileNet-V2)

- Input: 224 × 224 × 3, FP32 (ImageNet normalisation).
- Output: 1001-class softmax scores.
- Metric: Top-1 / Top-5 accuracy (when labels are available), latency,
  throughput.

### Object Detection (YOLOv8n)

- Input: 640 × 640 × 3, FP32 normalised to [0, 1].
- Output: Bounding boxes + confidence scores.
- Metric: Detection count, confidence distribution, latency, throughput.

### Image Enhancement (ESPCN-x2)

- Input: Grayscale, variable resolution (typically 128 × 128).
- Output: 2× upscaled image.
- Metric: PSNR, SSIM (when reference available), latency, throughput.

## Stress Testing

Runs continuous inference for a configurable duration (default 60 s)
while simultaneously stressing selected hardware components.

### Stress Targets

| Target | Workload Description |
| ------ | -------------------- |
| CPU | Heavy matrix operations (numpy dot products, SVD) in background threads |
| GPU | Large tensor multiplications to saturate GPU compute |
| Memory | Repeated 80 MB allocations with MD5 hashing to create memory pressure |
| Disk | Sequential 4 MB write/read cycles on every writable partition |
| Network | DNS lookups and TCP connection attempts to exercise the network stack |
| CPU + GPU | CPU and GPU stress combined |
| All | All five components stressed simultaneously |

Stress workers run as daemon threads alongside the inference loop. The
framework splits the collected latency trace into first-quarter and
last-quarter windows and computes:

- **Latency drift** — percentage change in mean latency.
- **Degradation detected** — `True` if drift exceeds 10%.

## Reliability Testing

Runs the same input through the model `N` times and checks:

- **Byte-level consistency** — SHA-256 of raw output buffers.
- **Numerical tolerance** — Maximum absolute difference vs. a tolerance
  threshold (default 1 × 10⁻⁵).

## Composite Scoring

Each benchmark result receives a composite score in [0, 100]:

```text
score = w_latency   × norm(latency)
      + w_throughput × norm(throughput)
      + w_resource   × norm(resource)
      + w_stability  × norm(stability)
```

| Component   | Weight | Ideal direction | Normalisation            |
|-------------|--------|-----------------|--------------------------|
| Latency     | 0.30   | Lower is better | 100 × (1 − clamp(v/100)) |
| Throughput  | 0.30   | Higher is better| 100 × clamp(v/200)       |
| Resource    | 0.20   | Lower is better | 100 × (1 − clamp(v/100)) |
| Stability   | 0.20   | Lower is better | 100 × (1 − clamp(v/0.5)) |

All normalisations are clamped to [0, 100] before weighting.

## Limitations

- Models are limited to three lightweight architectures optimised for
  integrated GPUs.
- GPU monitoring accuracy depends on driver-level reporting; Intel Iris Xe
  may expose limited telemetry compared to discrete GPUs.
- Thermal readings may be unavailable on some systems.
- Results are not directly comparable across different hardware platforms
  without the composite scoring normalisation.
