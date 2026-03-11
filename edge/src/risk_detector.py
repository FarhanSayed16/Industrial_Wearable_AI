"""
Industrial Wearable AI — Edge Risk Detector

Fatigue and ergonomic risk scoring at the edge using trained models.
Falls back to rule-based detection if models aren't available.
"""
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

FATIGUE_LABELS = ["normal", "mild", "high"]


class RiskDetector:
    """Detects fatigue and ergonomic risk from sensor features."""

    def __init__(
        self,
        fatigue_model_path: Optional[Path] = None,
        ergo_model_path: Optional[Path] = None,
    ):
        self.fatigue_model = self._load(fatigue_model_path, "fatigue")
        self.ergo_model = self._load(ergo_model_path, "ergo")

        # Rolling state for fatigue detection
        self._recent_labels: list[str] = []
        self._continuous_work_minutes = 0.0
        self._last_activity = "idle"
        self._motion_history: list[float] = []

    @staticmethod
    def _load(path: Optional[Path], name: str):
        if not path or not path.exists():
            logger.info("No %s model at %s — using rule-based fallback", name, path)
            return None
        try:
            import joblib
            model = joblib.load(path)
            logger.info("Loaded %s model from %s", name, path)
            return model
        except Exception as e:
            logger.warning("Failed to load %s model: %s", name, e)
            return None

    def update_rolling_state(self, label: str, interval_sec: float = 3.0):
        """Update rolling state with the latest classification result."""
        self._recent_labels.append(label)
        if len(self._recent_labels) > 200:  # ~10 min at 3s intervals
            self._recent_labels = self._recent_labels[-200:]

        if label in ("sewing", "adjusting"):
            self._continuous_work_minutes += interval_sec / 60.0
        elif label in ("break", "idle"):
            self._continuous_work_minutes = max(0, self._continuous_work_minutes - 0.5)

        self._last_activity = label

    def detect_fatigue(self, features: np.ndarray) -> tuple[str, float]:
        """
        Detect fatigue risk.
        Returns: (level: 'normal'|'mild'|'high', score: 0.0–1.0)
        """
        # Build fatigue features from rolling state
        fatigue_features = self._build_fatigue_features(features)

        if self.fatigue_model is not None:
            try:
                pred = self.fatigue_model.predict(fatigue_features.reshape(1, -1))[0]
                proba = self.fatigue_model.predict_proba(fatigue_features.reshape(1, -1))[0]
                level = FATIGUE_LABELS[int(pred)]
                score = float(proba[int(pred)])
                return level, score
            except Exception:
                pass

        # Rule-based fallback
        return self._rule_based_fatigue()

    def detect_ergo_risk(self, features: np.ndarray) -> tuple[str, float]:
        """
        Detect ergonomic risk.
        Returns: (level: 'low'|'medium'|'high', score: 0.0–100.0)
        """
        ergo_features = self._build_ergo_features(features)

        if self.ergo_model is not None:
            try:
                score = float(self.ergo_model.predict(ergo_features.reshape(1, -1))[0])
                score = max(0.0, min(100.0, score))
                level = "low" if score <= 30 else "medium" if score <= 60 else "high"
                return level, score
            except Exception:
                pass

        # Rule-based fallback
        return self._rule_based_ergo(features)

    def _build_fatigue_features(self, features: np.ndarray) -> np.ndarray:
        """Build 8-dim fatigue feature vector from rolling state + current features."""
        labels = self._recent_labels
        n = len(labels) if labels else 1

        # Motion decay: compare recent vs earlier activity levels
        mid = max(1, n // 2)
        early_active = sum(1 for l in labels[:mid] if l in ("sewing", "adjusting")) / max(mid, 1)
        late_active = sum(1 for l in labels[mid:] if l in ("sewing", "adjusting")) / max(n - mid, 1)
        motion_decay = late_active / max(early_active, 0.01)

        # State transitions
        transitions = sum(1 for i in range(1, n) if labels[i] != labels[i - 1])
        repetition_count = transitions

        # Ratios
        idle_count = sum(1 for l in labels if l in ("idle", "break"))
        idle_ratio = idle_count / max(n, 1)
        active_count = sum(1 for l in labels if l in ("sewing", "adjusting"))
        active_ratio = active_count / max(n, 1)

        # Features from current window
        std_indices = [1, 6, 11, 16, 21, 26]
        avg_accel_std = np.mean([float(features[i]) for i in std_indices if i < len(features)])

        return np.array([
            motion_decay,
            repetition_count,
            idle_ratio,
            active_ratio,
            avg_accel_std,
            0.0,  # temp_delta (needs temperature history, placeholder)
            self._continuous_work_minutes,
            0.0,  # zcr_trend (placeholder)
        ], dtype=np.float32)

    def _build_ergo_features(self, features: np.ndarray) -> np.ndarray:
        """Build 6-dim ergo feature vector from IMU features."""
        if len(features) < 30:
            return np.zeros(6, dtype=np.float32)

        # Approximate wrist angle from accelerometer mean values
        ax_mean, ay_mean, az_mean = float(features[0]), float(features[5]), float(features[10])
        wrist_angle = np.degrees(np.arctan2(np.sqrt(ax_mean**2 + az_mean**2), abs(ay_mean) + 0.01))

        # Hold duration approximation from std (low std = static posture)
        ax_std, ay_std = float(features[1]), float(features[6])
        hold_indicator = max(0, 30 - (ax_std + ay_std) * 50)

        # Repetitions from zero crossing rate
        zcr_indices = [4, 9, 14, 19, 24, 29]
        avg_zcr = np.mean([float(features[i]) for i in zcr_indices if i < len(features)])
        reps_per_min = avg_zcr * 60

        # Overall variance
        std_indices = [1, 6, 11, 16, 21, 26]
        accel_variance = np.mean([float(features[i]) for i in std_indices[:3]])

        # Gyro range
        gyro_max_indices = [18, 23, 28]
        gyro_min_indices = [17, 22, 27]
        gyro_range = sum(
            float(features[mx]) - float(features[mn])
            for mx, mn in zip(gyro_max_indices, gyro_min_indices)
            if mx < len(features) and mn < len(features)
        )

        # Asymmetry
        asymmetry = abs(float(features[0]) - float(features[5])) / (abs(float(features[0])) + abs(float(features[5])) + 0.01)
        asymmetry_ratio = 1.0 - asymmetry

        return np.array([
            wrist_angle, hold_indicator, reps_per_min,
            accel_variance, gyro_range, asymmetry_ratio,
        ], dtype=np.float32)

    def _rule_based_fatigue(self) -> tuple[str, float]:
        """Rule-based fatigue detection fallback."""
        if self._continuous_work_minutes > 90:
            return "high", 0.85
        if self._continuous_work_minutes > 45:
            return "mild", 0.65

        labels = self._recent_labels[-60:]  # Last ~3 minutes
        if labels:
            idle_ratio = sum(1 for l in labels if l in ("idle", "break")) / len(labels)
            if idle_ratio > 0.6:
                return "mild", 0.55

        return "normal", 0.90

    def _rule_based_ergo(self, features: np.ndarray) -> tuple[str, float]:
        """Rule-based ergonomic risk fallback."""
        if len(features) < 30:
            return "low", 10.0

        std_indices = [1, 6, 11]
        stds = [float(features[i]) for i in std_indices if i < len(features)]
        var_sum = sum(stds)

        if var_sum < 0.05:  # Very static — prolonged posture risk
            return "medium", 45.0
        if var_sum > 1.5:  # Very high motion — repetitive strain
            return "medium", 50.0

        return "low", 15.0
