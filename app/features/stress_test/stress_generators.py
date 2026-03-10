"""Stress generators — synthetic workloads that stress specific hardware components."""
from __future__ import annotations

import hashlib
import math
import os
import tempfile
import threading
import time
from typing import Callable, List, Optional

import numpy as np
import psutil

from app.config.constants import (
    STRESS_TARGET_CPU, STRESS_TARGET_GPU, STRESS_TARGET_MEMORY,
    STRESS_TARGET_NETWORK, STRESS_TARGET_DISK, STRESS_TARGET_CPU_GPU,
    STRESS_TARGET_ALL,
)
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class _StressWorker:
    """Runs a stress function in a background thread until stopped."""

    def __init__(self, name: str, fn: Callable[[], None]):
        self.name = name
        self._fn = fn
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name=f"stress-{self.name}")
        self._thread.start()
        logger.info("Stress worker '%s' started", self.name)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=10.0)
        logger.info("Stress worker '%s' stopped", self.name)

    def _loop(self) -> None:
        while self._running:
            try:
                self._fn()
            except Exception as e:
                logger.debug("Stress worker '%s' error: %s", self.name, e)


# ── Individual Stress Functions ───────────────────────────────────────


def _cpu_burn() -> None:
    """Burn CPU cycles with heavy math operations."""
    data = np.random.randn(500, 500)
    for _ in range(3):
        np.dot(data, data)
        np.linalg.svd(data[:100, :100], full_matrices=False)


def _gpu_burn() -> None:
    """Burn GPU with repeated small inference-like tensor operations.

    Falls back to CPU-heavy numpy if no GPU library is available.
    """
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            raise ImportError("No GPU")
    except (ImportError, Exception):
        pass
    # Use large matrix multiplies — on GPU-accelerated numpy this hits GPU,
    # otherwise it still generates measurable system load.
    data = np.random.randn(1024, 1024).astype(np.float32)
    for _ in range(5):
        np.dot(data, data)


def _memory_pressure() -> None:
    """Allocate and touch memory to create memory pressure."""
    blocks = []
    try:
        for _ in range(10):
            block = np.random.bytes(8 * 1024 * 1024)  # 8 MB blocks
            _ = hashlib.md5(block).hexdigest()
            blocks.append(block)
        time.sleep(0.1)
    finally:
        del blocks


def _disk_stress() -> None:
    """Write and read temporary files across all writable partitions."""
    partitions = psutil.disk_partitions(all=False)
    for part in partitions:
        try:
            mount = part.mountpoint
            test_dir = os.path.join(mount, ".bench_stress_tmp")
            os.makedirs(test_dir, exist_ok=True)
            fpath = os.path.join(test_dir, "stress_io.bin")
            # Write 4 MB
            data = os.urandom(4 * 1024 * 1024)
            with open(fpath, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            # Read back
            with open(fpath, "rb") as f:
                _ = f.read()
            os.remove(fpath)
            os.rmdir(test_dir)
        except (PermissionError, OSError) as e:
            logger.debug("Skipping partition %s: %s", part.mountpoint, e)
            continue


def _network_stress() -> None:
    """Generate network I/O by performing DNS lookups and small HTTP fetches.

    Uses only loopback / local-stack traffic when external access fails.
    """
    import socket
    hosts = ["localhost", "127.0.0.1"]
    for host in hosts:
        try:
            socket.getaddrinfo(host, 80)
        except socket.gaierror:
            pass
    # TCP connect to loopback ports to exercise network stack
    for port in range(49152, 49162):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.05)
            s.connect_ex(("127.0.0.1", port))
            s.close()
        except OSError:
            pass
    time.sleep(0.05)


# ── Target → Workers mapping ─────────────────────────────────────────

_TARGET_FUNCTIONS = {
    STRESS_TARGET_CPU: [("cpu", _cpu_burn)],
    STRESS_TARGET_GPU: [("gpu", _gpu_burn)],
    STRESS_TARGET_MEMORY: [("memory", _memory_pressure)],
    STRESS_TARGET_NETWORK: [("network", _network_stress)],
    STRESS_TARGET_DISK: [("disk", _disk_stress)],
    STRESS_TARGET_CPU_GPU: [("cpu", _cpu_burn), ("gpu", _gpu_burn)],
    STRESS_TARGET_ALL: [
        ("cpu", _cpu_burn),
        ("gpu", _gpu_burn),
        ("memory", _memory_pressure),
        ("network", _network_stress),
        ("disk", _disk_stress),
    ],
}


class StressManager:
    """Manages background stress workers for a given target configuration."""

    def __init__(self, target: str):
        self.target = target
        self._workers: List[_StressWorker] = []

    def start(self) -> None:
        funcs = _TARGET_FUNCTIONS.get(self.target, [])
        if not funcs:
            logger.warning("Unknown stress target '%s', no extra stress applied", self.target)
            return
        for name, fn in funcs:
            worker = _StressWorker(name, fn)
            self._workers.append(worker)
            worker.start()
        logger.info("StressManager started %d workers for target '%s'", len(self._workers), self.target)

    def stop(self) -> None:
        for worker in self._workers:
            worker.stop()
        self._workers.clear()
        logger.info("StressManager stopped all workers for target '%s'", self.target)
