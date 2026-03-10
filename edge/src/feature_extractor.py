"""
Industrial Wearable AI — Feature Extraction
Per-axis: mean, std, min, max, zero_crossing_rate. Output: 30-dim vector.
Must match ml/scripts/feature_extraction.py exactly for training/inference consistency.
"""
import numpy as np
from typing import List


AXES = ["ax", "ay", "az", "gx", "gy", "gz"]
FEATURES_PER_AXIS = 5  # mean, std, min, max, zero_crossing_rate
FEATURE_DIM = len(AXES) * FEATURES_PER_AXIS  # 30


def _zero_crossing_rate(arr: np.ndarray) -> float:
    """Count sign changes / (2 * (n-1)) per MASTER_PLAN."""
    if len(arr) < 2:
        return 0.0
    signs = np.sign(arr)
    changes = np.sum(np.abs(np.diff(signs))) // 2  # each change contributes 2 to abs(diff)
    return changes / (2 * (len(arr) - 1))


def extract_features(samples: List[dict]) -> np.ndarray:
    """
    Extract 30 features from samples. Input: list of dicts with ax, ay, az, gx, gy, gz.
    Output: 1D array of 30 floats (6 axes × 5 features).
    """
    if not samples:
        return np.zeros(FEATURE_DIM, dtype=np.float32)

    features = []
    for axis in AXES:
        arr = np.array([s.get(axis, 0) for s in samples], dtype=np.float64)
        mean_val = np.mean(arr)
        std_val = np.std(arr)
        if np.isnan(std_val) or std_val == 0:
            std_val = 1e-8
        min_val = np.min(arr)
        max_val = np.max(arr)
        zcr = _zero_crossing_rate(arr)
        features.extend([mean_val, std_val, min_val, max_val, zcr])

    return np.array(features, dtype=np.float32)
