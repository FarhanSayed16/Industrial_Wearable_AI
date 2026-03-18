#!/usr/bin/env python3
"""
Industrial Wearable AI — Ergonomic Risk Scorer Training Script

Hybrid model: rule-based features + logistic regression.
Outputs a continuous ergonomic risk score (0–100) based on:
  - Wrist angle deviation (derived from accelerometer pitch/roll)
  - Hold duration (time in static posture)
  - Repetition frequency (state transitions per minute)
  - Acceleration variance (repetitive strain indicator)

Score mapping:
  0–30  = Low risk
  31–60 = Medium risk
  61–100 = High risk

Model saved to: ml/models/ergo_model.joblib
"""
import json
import sys
from pathlib import Path

import numpy as np

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

MODEL_OUT = _root / "ml" / "models" / "ergo_model.joblib"
FEATURE_NAMES = [
    "wrist_angle_deviation",    # degrees from neutral (derived from accel)
    "hold_duration_seconds",    # time in same posture
    "repetitions_per_minute",   # state changes per minute
    "accel_variance",           # overall motion variance
    "gyro_range",               # max - min gyroscope reading
    "asymmetry_ratio",          # left-right acceleration asymmetry
]


def generate_synthetic_data(n_samples: int = 1500, seed: int = 42) -> tuple:
    """Generate synthetic ergonomic risk data."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.float32)  # 0–100 score

    for i in range(n_samples):
        risk = rng.choice(["low", "medium", "high"], p=[0.5, 0.3, 0.2])

        if risk == "low":
            X[i] = [
                rng.uniform(0, 15),       # wrist_angle small
                rng.uniform(0, 10),       # hold_duration short
                rng.uniform(8, 20),       # repetitions moderate
                rng.uniform(0.2, 0.6),    # accel_variance normal
                rng.uniform(50, 200),     # gyro_range moderate
                rng.uniform(0.8, 1.0),    # asymmetry_ratio balanced
            ]
            y[i] = rng.uniform(0, 30)
        elif risk == "medium":
            X[i] = [
                rng.uniform(12, 35),      # wrist_angle moderate
                rng.uniform(8, 30),       # hold_duration longer
                rng.uniform(18, 35),      # repetitions high
                rng.uniform(0.1, 0.4),    # accel_variance lower (fixed posture)
                rng.uniform(30, 120),     # gyro_range lower
                rng.uniform(0.5, 0.85),   # asymmetry_ratio imbalanced
            ]
            y[i] = rng.uniform(30, 65)
        else:
            X[i] = [
                rng.uniform(30, 60),      # wrist_angle extreme
                rng.uniform(25, 90),      # hold_duration very long
                rng.uniform(28, 50),      # repetitions very high
                rng.uniform(0.05, 0.25),  # accel_variance very low
                rng.uniform(10, 80),      # gyro_range restricted
                rng.uniform(0.3, 0.6),    # asymmetry_ratio very imbalanced
            ]
            y[i] = rng.uniform(60, 100)

    return X, y


def train():
    """Train the ergonomic risk scoring model."""
    print("=" * 60)
    print("  Ergonomic Risk Scorer — Training")
    print("=" * 60)

    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import cross_val_score
    import joblib

    X, y = generate_synthetic_data()
    print(f"  Samples: {len(X)} | Features: {X.shape[1]}")
    print(f"  Score range: {y.min():.1f} – {y.max():.1f}")

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", Ridge(alpha=1.0)),
    ])

    scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    print(f"  Cross-val R²: {scores.mean():.3f} ± {scores.std():.3f}")

    model.fit(X, y)

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    print(f"  Model saved → {MODEL_OUT}")

    meta = {
        "features": FEATURE_NAMES,
        "output": "ergo_score (0-100)",
        "thresholds": {"low": [0, 30], "medium": [31, 60], "high": [61, 100]},
    }
    meta_path = MODEL_OUT.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved → {meta_path}")
    print("  Done ✓")


if __name__ == "__main__":
    train()
