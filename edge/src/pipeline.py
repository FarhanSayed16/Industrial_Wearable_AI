"""
Industrial Wearable AI — Processing Pipeline
Low-pass filter + feature extraction. process_window returns 30-dim feature vector.
"""
from typing import List, Optional

import numpy as np

from .feature_extractor import extract_features

# Low-pass: exponential moving average alpha
DEFAULT_ALPHA = 0.3


def _lowpass_filter(arr: np.ndarray, alpha: float = DEFAULT_ALPHA) -> np.ndarray:
    """Exponential moving average on 1D array."""
    out = np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return out


def process_window(
    samples: List[dict],
    alpha: float = DEFAULT_ALPHA,
) -> np.ndarray:
    """
    Apply low-pass filter to each axis, then extract features.
    Returns 30-dim feature vector.
    """
    if not samples:
        return np.zeros(30, dtype=np.float32)

    axes = ["ax", "ay", "az", "gx", "gy", "gz"]
    filtered = []
    for s in samples:
        row = {}
        for axis in axes:
            arr = np.array([x.get(axis, 0) for x in samples], dtype=np.float64)
            row[axis] = _lowpass_filter(arr, alpha)[-1]  # Use last filtered value per sample
        filtered.append(row)

    # Actually: we need to filter the whole sequence per axis, then build filtered samples
    filtered_samples = []
    for i in range(len(samples)):
        row = {}
        for axis in axes:
            arr = np.array([s.get(axis, 0) for s in samples], dtype=np.float64)
            filt = _lowpass_filter(arr, alpha)
            row[axis] = filt[i]
        filtered_samples.append(row)

    return extract_features(filtered_samples)
