"""Application-wide constants."""

APP_NAME = "AI Workload Benchmarking Framework"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "For Integrated & Mid-Range Graphics Systems"

# ── Workload types ─────────────────────────────────────────────────────
WORKLOAD_CLASSIFICATION = "classification"
WORKLOAD_DETECTION = "detection"
WORKLOAD_ENHANCEMENT = "enhancement"
WORKLOAD_GENAI = "genai"
WORKLOAD_STRESS = "stress_test"
WORKLOAD_RELIABILITY = "reliability"

ALL_WORKLOADS = [
    WORKLOAD_CLASSIFICATION,
    WORKLOAD_DETECTION,
    WORKLOAD_ENHANCEMENT,
    WORKLOAD_GENAI,
    WORKLOAD_STRESS,
    WORKLOAD_RELIABILITY,
]

WORKLOAD_LABELS = {
    WORKLOAD_CLASSIFICATION: "Image Classification",
    WORKLOAD_DETECTION: "Object Detection",
    WORKLOAD_ENHANCEMENT: "Image Enhancement",
    WORKLOAD_GENAI: "Generative AI (LLM)",
    WORKLOAD_STRESS: "Stress Test",
    WORKLOAD_RELIABILITY: "Reliability Test",
}

# ── Backend types ──────────────────────────────────────────────────────
BACKEND_OPENVINO = "openvino"
BACKEND_ONNX = "onnxruntime"

ALL_BACKENDS = [BACKEND_OPENVINO, BACKEND_ONNX]

BACKEND_LABELS = {
    BACKEND_OPENVINO: "OpenVINO",
    BACKEND_ONNX: "ONNX Runtime",
}

# ── Device types ───────────────────────────────────────────────────────
DEVICE_CPU = "CPU"
DEVICE_GPU = "GPU"
DEVICE_AUTO = "AUTO"

# ── Model registry ────────────────────────────────────────────────────
CLASSIFICATION_MODELS = {
    "mobilenet-v2": {
        "name": "MobileNet V2",
        "input_size": (224, 224),
        "openvino_model": "classification/mobilenet-v2-pytorch/FP16/mobilenet-v2-pytorch.xml",
        "onnx_model": "classification/mobilenet-v2.onnx",
        "labels": "classification/imagenet_labels.txt",
    },
}

DETECTION_MODELS = {
    "yolov8n": {
        "name": "YOLOv8n",
        "input_size": (640, 640),
        "onnx_model": "detection/yolov8n.onnx",
        "labels": "detection/coco_labels.txt",
    },
}

ENHANCEMENT_MODELS = {
    "espcn-x2": {
        "name": "ESPCN x3",
        "scale": 3,
        "onnx_model": "enhancement/espcn_x2.onnx",
    },
}

GENAI_MODELS = {
    "tinyllama-1.1b-chat": {
        "name": "TinyLlama 1.1B Chat (INT4)",
        "hf_repo": "OpenVINO/TinyLlama-1.1B-Chat-v1.0-int4-ov",
        "local_path": "genai/tinyllama-1.1b-chat-int4-ov",
        "required_ram_mb": 2000,
    },
    "phi-3-mini-4k-instruct": {
        "name": "Phi-3-Mini-4K-Instruct (INT4)",
        "hf_repo": "OpenVINO/Phi-3-mini-4k-instruct-int4-ov",
        "local_path": "genai/phi-3-mini-4k-instruct-int4-ov",
        "required_ram_mb": 4500,
    },
    "llama-3-8b-instruct": {
        "name": "Llama-3-8B-Instruct (INT4)",
        "hf_repo": "OpenVINO/llama-3-8b-instruct-int4-ov",
        "local_path": "genai/llama-3-8b-instruct-int4-ov",
        "required_ram_mb": 8000,
    },
}

# ── Monitoring ─────────────────────────────────────────────────────────
MONITOR_SAMPLE_INTERVAL = 0.5  # seconds

# ── Stress Targets ─────────────────────────────────────────────────────
STRESS_TARGET_CPU = "cpu"
STRESS_TARGET_GPU = "gpu"
STRESS_TARGET_MEMORY = "memory"
STRESS_TARGET_NETWORK = "network"
STRESS_TARGET_DISK = "disk"
STRESS_TARGET_CPU_GPU = "cpu_gpu"
STRESS_TARGET_ALL = "all"

ALL_STRESS_TARGETS = [
    STRESS_TARGET_CPU,
    STRESS_TARGET_GPU,
    STRESS_TARGET_MEMORY,
    STRESS_TARGET_NETWORK,
    STRESS_TARGET_DISK,
    STRESS_TARGET_CPU_GPU,
    STRESS_TARGET_ALL,
]

STRESS_TARGET_LABELS = {
    STRESS_TARGET_CPU: "CPU",
    STRESS_TARGET_GPU: "GPU",
    STRESS_TARGET_MEMORY: "Memory",
    STRESS_TARGET_NETWORK: "Network (Wi-Fi/Ethernet)",
    STRESS_TARGET_DISK: "Disk (All Partitions)",
    STRESS_TARGET_CPU_GPU: "CPU + GPU",
    STRESS_TARGET_ALL: "All Combined",
}

# ── Analysis ───────────────────────────────────────────────────────────
P95_PERCENTILE = 95
CONSISTENCY_TOLERANCE = 1e-5
