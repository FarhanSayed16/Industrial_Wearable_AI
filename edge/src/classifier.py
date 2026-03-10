"""
Industrial Wearable AI — Activity Classifier
Load joblib model or use rule-based fallback. Labels match backend enum.
"""
import os
from pathlib import Path
from typing import Optional, Union

import numpy as np

LABELS = ["sewing", "idle", "adjusting", "error", "break"]


def load_model(path: Optional[Union[str, Path]]) -> Optional[object]:
    """Load joblib model if path exists; else return None."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        import joblib
        return joblib.load(p)
    except Exception:
        return None


def predict(model: Optional[object], features: np.ndarray) -> str:
    """
    Predict label. If model: use model.predict; map index to label.
    If no model: rule-based (variance heuristic).
    """
    if model is not None:
        try:
            pred = model.predict(features.reshape(1, -1))[0]
            if hasattr(model, "classes_"):
                idx = int(pred) if isinstance(pred, (int, np.integer)) else np.argmax(pred)
                if 0 <= idx < len(model.classes_):
                    label = str(model.classes_[idx]).lower()
                    return label if label in LABELS else LABELS[0]
            # Fallback: assume pred is index
            idx = int(pred) if isinstance(pred, (int, np.integer)) else 0
            return LABELS[idx % len(LABELS)]
        except Exception:
            pass

    # Rule-based fallback: use variance (sum of std features at indices 1,6,11,16,21,26)
    return _rule_based_predict(features)


def _rule_based_predict(features: np.ndarray) -> str:
    """
    Low variance → idle, higher → adjusting, highest → sewing.
    Thresholds tuned so normal sewing motion (IMU in g and deg/s) shows as working.
    Uses both sum of std (all axes) and max single-axis std so one moving axis is enough.
    """
    if len(features) < 30:
        return "idle"
    # Std features at indices 1, 6, 11, 16, 21, 26 (ax, ay, az, gx, gy, gz)
    std_indices = [1, 6, 11, 16, 21, 26]
    stds = [float(features[i]) for i in std_indices if i < len(features)]
    var_sum = sum(stds)
    var_max = max(stds) if stds else 0.0
    # Any noticeable motion on one axis → at least adjusting (then sewing if more)
    if var_sum < 0.06 and var_max < 0.12:
        return "idle"
    if var_sum < 0.25 and var_max < 0.5:
        return "adjusting"
    return "sewing"


def predict_with_confidence(model: Optional[object], features: np.ndarray) -> tuple:
    """
    Predict label WITH confidence score.
    Returns: (label: str, confidence: float 0.0–1.0)
    Confidence < 0.7 indicates low-confidence predictions suitable for human review.
    """
    if model is not None:
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features.reshape(1, -1))[0]
                pred_idx = int(np.argmax(proba))
                confidence = float(proba[pred_idx])
                if hasattr(model, "classes_"):
                    label = str(model.classes_[pred_idx]).lower()
                    label = label if label in LABELS else LABELS[pred_idx % len(LABELS)]
                else:
                    label = LABELS[pred_idx % len(LABELS)]
                return label, confidence

            # Model without predict_proba
            label = predict(model, features)
            return label, 0.8  # Default confidence for models without proba
        except Exception:
            pass

    # Rule-based: return with moderate confidence
    label = _rule_based_predict(features)
    confidence = 0.75 if label != "idle" else 0.85
    return label, confidence
