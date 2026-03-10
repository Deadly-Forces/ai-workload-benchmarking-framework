"""Resource sampler — collects monitoring samples in a background thread."""

from __future__ import annotations

import time
import threading
from typing import List

from app.config.constants import MONITOR_SAMPLE_INTERVAL
from app.config.logging_config import get_logger
from app.features.monitoring.schemas import MonitorSample, MonitoringData
from app.features.monitoring.cpu_monitor import get_cpu_percent
from app.features.monitoring.memory_monitor import (
    get_memory_percent,
    get_process_memory_mb,
)
from app.features.monitoring.gpu_monitor import get_gpu_usage
from app.features.monitoring.thermal_monitor import get_temperature

logger = get_logger(__name__)


class ResourceSampler:
    """Background resource sampler that collects system metrics during benchmark execution."""

    def __init__(self, interval: float = MONITOR_SAMPLE_INTERVAL):
        self.interval = interval
        self._samples: List[MonitorSample] = []
        self._running = False
        self._thread: threading.Thread | None = None
        self._start_time: float = 0.0

    def start(self) -> None:
        """Start background sampling."""
        self._samples.clear()
        self._running = True
        self._start_time = time.perf_counter()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        logger.info("Resource sampler started (interval=%.1fs)", self.interval)

    def stop(self) -> MonitoringData:
        """Stop sampling and return collected data."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        duration = time.perf_counter() - self._start_time
        logger.info(
            "Resource sampler stopped (%d samples, %.1fs)", len(self._samples), duration
        )
        return MonitoringData(
            samples=list(self._samples),
            sample_interval=self.interval,
            duration_seconds=duration,
        )

    def _sample_loop(self) -> None:
        """Sampling loop that runs in a background thread."""
        while self._running:
            try:
                gpu_pct, gpu_mem = get_gpu_usage()
                sample = MonitorSample(
                    timestamp=time.perf_counter() - self._start_time,
                    cpu_percent=get_cpu_percent(),
                    memory_percent=get_memory_percent(),
                    memory_mb=get_process_memory_mb(),
                    gpu_percent=gpu_pct,
                    gpu_memory_mb=gpu_mem,
                    temperature_c=get_temperature(),
                )
                self._samples.append(sample)
            except Exception as e:
                logger.debug("Sampling error: %s", e)
            time.sleep(self.interval)

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    @property
    def latest_sample(self) -> MonitorSample | None:
        return self._samples[-1] if self._samples else None

    def get_current_samples(self) -> List[MonitorSample]:
        """Return a copy of the samples collected so far."""
        return list(self._samples)
