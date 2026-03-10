"""Anomaly detection for system metrics during benchmarks."""

from __future__ import annotations

from typing import List, Dict, Any

from app.config.logging_config import get_logger
from app.features.monitoring.sampler import MonitorSample

logger = get_logger(__name__)

try:
    from sklearn.ensemble import IsolationForest

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Anomaly detection will be disabled.")


class AnomalyDetector:
    """Detects system anomalies (like background interference) during benchmarks."""

    def __init__(self, contamination: float = 0.05):
        """Initialize the detector.

        Args:
            contamination: The proportion of outliers in the data set. Used for training.
        """
        self.model = (
            IsolationForest(contamination=contamination, random_state=42)
            if SKLEARN_AVAILABLE
            else None
        )

        self.is_trained = False
        self.anomalies_detected = 0

    def _extract_features(self, sample: MonitorSample) -> List[float]:
        return [
            float(sample.cpu_percent),
            float(sample.memory_percent),
            float(sample.temperature_c if sample.temperature_c is not None else 0.0),
        ]

    def train_baseline_profile(self, baseline_samples: List[MonitorSample]) -> None:
        """Train the baseline profile on known good/normal samples (e.g. warmup phase)."""
        if not SKLEARN_AVAILABLE or not baseline_samples:
            return

        features = [self._extract_features(s) for s in baseline_samples]
        if len(features) < 3:
            logger.warning(
                "Not enough samples to train baseline profile (minimum 3 required)."
            )
            return

        try:
            self.model.fit(features)
            self.is_trained = True
            logger.info(
                "Anomaly detector trained on %d baseline samples", len(features)
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to train anomaly detector: %s", e)
            self.is_trained = False

    def detect_system_anomalies(
        self, recent_samples: List[MonitorSample]
    ) -> Dict[str, Any]:
        """Check a stream of live samples against the baseline.

        Returns:
            Dictionary with anomaly indicators.
        """
        result = {"has_anomaly": False, "anomaly_indices": [], "message": ""}

        if not self.is_trained or not recent_samples:
            return result

        features = [self._extract_features(s) for s in recent_samples]

        try:
            preds = self.model.predict(features)
            # IsolationForest returns -1 for anomalies, 1 for normal
            anomalous_idx = [i for i, pred in enumerate(preds) if pred == -1]

            if anomalous_idx:
                self.anomalies_detected += len(anomalous_idx)
                result["has_anomaly"] = True
                result["anomaly_indices"] = anomalous_idx
                result["message"] = (
                    f"Detected {len(anomalous_idx)} anomalous resource spikes/drops."
                )
                logger.warning(result["message"])

            return result

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Anomaly detection failed: %s", e)
            return result
