#!/usr/bin/env python3
"""
Industrial Wearable AI — Fatigue Predictor Training Script

Trains an XGBoost model that predicts fatigue risk level from rolling
10-minute feature windows. The model outputs probability scores that are
thresholded into Normal / Mild / High fatigue risk.

Features (derived from activity_events over rolling windows):
  - motion_decay: ratio of avg motion in last 2 min vs first 2 min
  - repetition_count: number of state transitions in the window
  - idle_ratio: fraction of time spent idle
  - active_ratio: fraction of time in sewing/adjusting
  - avg_accel_std: average acceleration standard deviation
  - temp_delta: temperature change over the window
  - continuous_work_minutes: consecutive minutes without break
  - zcr_trend: trend of zero-crossing rate (increasing = shakier movements)

Output: 0 = Normal, 1 = Mild, 2 = High fatigue risk
Model saved to: ml/models/fatigue_model.joblib
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

# Add project root
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

MODEL_OUT = _root / "ml" / "models" / "fatigue_model.joblib"
FEATURE_NAMES = [
    "motion_decay", "repetition_count", "idle_ratio", "active_ratio",
    "avg_accel_std", "temp_delta", "continuous_work_minutes", "zcr_trend",
]


def generate_synthetic_data(n_samples: int = 2000, seed: int = 42) -> tuple:
    """
    Generate synthetic training data since real labeled fatigue data
    requires long-term collection. Patterns follow ergonomic research:
    - Normal: high motion, low idle, short continuous work
    - Mild: declining motion, moderate idle, moderate work duration
    - High: very low motion, high idle, long continuous work
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.int32)

    for i in range(n_samples):
        label = rng.choice([0, 0, 0, 1, 1, 2], p=[0.35, 0.15, 0.1, 0.15, 0.1, 0.15])
        y[i] = label

        if label == 0:  # Normal
            X[i] = [
                rng.uniform(0.8, 1.2),    # motion_decay ~ stable
                rng.integers(5, 25),       # repetition_count
                rng.uniform(0.05, 0.2),    # idle_ratio low
                rng.uniform(0.6, 0.9),     # active_ratio high
                rng.uniform(0.3, 0.8),     # avg_accel_std moderate
                rng.uniform(-0.5, 0.5),    # temp_delta stable
                rng.uniform(5, 45),        # continuous_work_minutes
                rng.uniform(-0.1, 0.1),    # zcr_trend stable
            ]
        elif label == 1:  # Mild
            X[i] = [
                rng.uniform(0.5, 0.85),    # motion_decay declining
                rng.integers(3, 15),       # repetition_count lower
                rng.uniform(0.15, 0.4),    # idle_ratio moderate
                rng.uniform(0.4, 0.65),    # active_ratio moderate
                rng.uniform(0.15, 0.45),   # avg_accel_std lower
                rng.uniform(0.3, 1.0),     # temp_delta rising
                rng.uniform(40, 90),       # continuous_work_minutes longer
                rng.uniform(0.05, 0.2),    # zcr_trend slightly rising
            ]
        else:  # High
            X[i] = [
                rng.uniform(0.2, 0.55),    # motion_decay significant decline
                rng.integers(1, 8),        # repetition_count very low
                rng.uniform(0.35, 0.7),    # idle_ratio high
                rng.uniform(0.15, 0.45),   # active_ratio low
                rng.uniform(0.05, 0.2),    # avg_accel_std very low
                rng.uniform(0.5, 1.5),     # temp_delta significant rise
                rng.uniform(80, 180),      # continuous_work_minutes very long
                rng.uniform(0.15, 0.4),    # zcr_trend rising (shakier)
            ]

    return X, y


def train():
    """Train the fatigue prediction model."""
    print("=" * 60)
    print("  Fatigue Predictor — Training")
    print("=" * 60)

    try:
        from xgboost import XGBClassifier
    except ImportError:
        from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
        print("⚠  xgboost not installed, using sklearn GradientBoostingClassifier")

    from sklearn.model_selection import cross_val_score
    import joblib

    X, y = generate_synthetic_data()
    print(f"  Samples: {len(X)} | Features: {X.shape[1]}")
    print(f"  Class distribution: Normal={np.sum(y == 0)}, Mild={np.sum(y == 1)}, High={np.sum(y == 2)}")

    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    ) if "XGBClassifier" in str(type) else XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )

    # Use sklearn-compatible API
    try:
        model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
    except TypeError:
        model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
        )

    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"  Cross-val accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

    model.fit(X, y)

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    print(f"  Model saved → {MODEL_OUT}")

    # Save feature names for reference
    meta = {"features": FEATURE_NAMES, "classes": ["normal", "mild", "high"]}
    meta_path = MODEL_OUT.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved → {meta_path}")
    print("  Done ✓")


if __name__ == "__main__":
    train()
