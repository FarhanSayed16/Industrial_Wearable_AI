"""
Industrial Wearable AI — Edge Anomaly Detector

Detects unusual motion patterns using an Isolation Forest model.
Falls back to simple statistical checks if the model isn't available.
"""
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalous motion patterns from 30-dim feature vectors."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model = self._load(model_path)
        self._recent_scores: list[float] = []

    @staticmethod
    def _load(path: Optional[Path]):
        if not path or not path.exists():
            logger.info("No anomaly model at %s — using statistical fallback", path)
            return None
        try:
            import joblib
            model = joblib.load(path)
            logger.info("Loaded anomaly model from %s", path)
            return model
        except Exception as e:
            logger.warning("Failed to load anomaly model: %s", e)
            return None

    def detect(self, features: np.ndarray) -> tuple[bool, float]:
        """
        Check if the current feature vector is anomalous.
        Returns: (is_anomaly: bool, anomaly_score: float)
                  anomaly_score: lower = more anomalous (Isolation Forest convention)
        """
        if self.model is not None:
            try:
                pred = self.model.predict(features.reshape(1, -1))[0]
                score = self.model.score_samples(features.reshape(1, -1))[0]
                is_anomaly = pred == -1
                return is_anomaly, float(score)
            except Exception:
                pass

        # Statistical fallback
        return self._statistical_check(features)

    def _statistical_check(self, features: np.ndarray) -> tuple[bool, float]:
        """Simple anomaly check: flag extreme feature values."""
        if len(features) < 30:
            return False, 0.0

        # Check for extreme values (more than 4 std from typical range)
        std_indices = [1, 6, 11, 16, 21, 26]
        stds = [float(features[i]) for i in std_indices if i < len(features)]

        # Very extreme motion or complete stillness with high gyro
        max_std = max(stds) if stds else 0
        min_std = min(stds) if stds else 0

        # All zeros (sensor failure)
        if np.allclose(features, 0, atol=1e-6):
            return True, -0.9

        # Extreme values
        if max_std > 5.0 or (max_std > 3.0 and min_std < 0.001):
            return True, -0.5

        return False, 0.1
