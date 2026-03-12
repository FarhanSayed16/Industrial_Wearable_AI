"""
Industrial Wearable AI — Feature Extraction (ML Training)
Same logic as edge/src/feature_extractor.py. Used for training pipeline consistency.
"""
import numpy as np
import pandas as pd
from typing import List, Union

AXES = ["ax", "ay", "az", "gx", "gy", "gz"]
FEATURES_PER_AXIS = 5
FEATURE_DIM = len(AXES) * FEATURES_PER_AXIS  # 30
DEFAULT_ALPHA = 0.3  # Match edge pipeline low-pass


def _zero_crossing_rate(arr: np.ndarray) -> float:
    """Count sign changes / (2 * (n-1))."""
    if len(arr) < 2:
        return 0.0
    signs = np.sign(arr)
    changes = int(np.sum(np.abs(np.diff(signs))) // 2)
    return changes / (2 * (len(arr) - 1))


def extract_features(samples: Union[List[dict], np.ndarray]) -> np.ndarray:
    """
    Extract 30 features. Input: list of dicts with ax,ay,az,gx,gy,gz, or DataFrame rows.
    Output: 1D array of 30 floats.
    """
    if not samples:
        return np.zeros(FEATURE_DIM, dtype=np.float32)

    if hasattr(samples[0], "get"):
        # List of dicts
        data = [{a: s.get(a, 0) for a in AXES} for s in samples]
    else:
        # Assume array-like with columns ax,ay,az,gx,gy,gz
        data = [dict(zip(AXES, row)) for row in samples]

    features = []
    for axis in AXES:
        arr = np.array([d.get(axis, 0) for d in data], dtype=np.float64)
        std_val = np.std(arr)
        if np.isnan(std_val) or std_val == 0:
            std_val = 1e-8
        features.extend([
            float(np.mean(arr)),
            float(std_val),
            float(np.min(arr)),
            float(np.max(arr)),
            _zero_crossing_rate(arr),
        ])
    return np.array(features, dtype=np.float32)


def _lowpass_filter(arr: np.ndarray, alpha: float = DEFAULT_ALPHA) -> np.ndarray:
    """Exponential moving average (match edge pipeline)."""
    out = np.empty_like(arr, dtype=np.float64)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return out


def extract_features_from_window(df: pd.DataFrame, apply_lowpass: bool = True) -> np.ndarray:
    """
    Extract 30 features from DataFrame window. Same logic as edge.
    Input: DataFrame with ax, ay, az, gx, gy, gz columns.
    """
    if df is None or len(df) == 0:
        return np.zeros(FEATURE_DIM, dtype=np.float32)
    data = df[AXES].values if all(a in df.columns for a in AXES) else np.zeros((len(df), 6))
    if apply_lowpass:
        filtered = []
        for j in range(6):
            col = data[:, j]
            filtered.append(_lowpass_filter(col))
        data = np.column_stack(filtered)
    samples = [dict(zip(AXES, data[i])) for i in range(len(data))]
    return extract_features(samples)
