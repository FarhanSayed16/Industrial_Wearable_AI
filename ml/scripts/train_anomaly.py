#!/usr/bin/env python3
"""
Industrial Wearable AI — Anomaly Detection Training Script

Trains an Isolation Forest model to detect unusual motion patterns.
Anomalies include: sudden stops after sustained activity, extreme
temperature spikes, or motion profiles that don't match any known
activity class.

Uses the same 30-dim feature vector as the activity classifier.
Model saved to: ml/models/anomaly_model.joblib
"""
import json
import sys
from pathlib import Path

import numpy as np

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

MODEL_OUT = _root / "ml" / "models" / "anomaly_model.joblib"


def generate_normal_data(n_samples: int = 2000, seed: int = 42) -> np.ndarray:
    """
    Generate synthetic 'normal' 30-dim feature vectors that represent
    typical sewing, idle, and adjusting patterns.
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n_samples, 30), dtype=np.float32)

    for i in range(n_samples):
        pattern = rng.choice(["sewing", "idle", "adjusting"], p=[0.5, 0.3, 0.2])

        for axis in range(6):
            base = axis * 5
            if pattern == "sewing":
                X[i, base + 0] = rng.normal(0, 0.5)       # mean
                X[i, base + 1] = rng.uniform(0.3, 1.2)    # std (high)
                X[i, base + 2] = rng.normal(-1.5, 0.5)    # min
                X[i, base + 3] = rng.normal(1.5, 0.5)     # max
                X[i, base + 4] = rng.uniform(0.1, 0.4)    # zcr
            elif pattern == "idle":
                X[i, base + 0] = rng.normal(0, 0.1)       # mean (stable)
                X[i, base + 1] = rng.uniform(0.01, 0.08)  # std (very low)
                X[i, base + 2] = rng.normal(-0.1, 0.05)   # min
                X[i, base + 3] = rng.normal(0.1, 0.05)    # max
                X[i, base + 4] = rng.uniform(0, 0.05)     # zcr
            else:  # adjusting
                X[i, base + 0] = rng.normal(0, 0.3)
                X[i, base + 1] = rng.uniform(0.1, 0.4)
                X[i, base + 2] = rng.normal(-0.8, 0.3)
                X[i, base + 3] = rng.normal(0.8, 0.3)
                X[i, base + 4] = rng.uniform(0.05, 0.2)

    return X


def train():
    """Train the anomaly detection model."""
    print("=" * 60)
    print("  Anomaly Detector — Training")
    print("=" * 60)

    from sklearn.ensemble import IsolationForest
    import joblib

    X_normal = generate_normal_data()
    print(f"  Normal samples: {len(X_normal)} | Features: {X_normal.shape[1]}")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # Expect 5% anomalies
        max_features=0.8,
        random_state=42,
    )
    model.fit(X_normal)

    # Test: generate some anomalous data
    rng = np.random.default_rng(99)
    X_anomaly = rng.uniform(-5, 5, size=(100, 30)).astype(np.float32)
    preds_normal = model.predict(X_normal[:100])
    preds_anomaly = model.predict(X_anomaly)
    normal_ok = np.mean(preds_normal == 1)
    anomaly_ok = np.mean(preds_anomaly == -1)
    print(f"  Normal correctly classified: {normal_ok:.1%}")
    print(f"  Anomaly correctly classified: {anomaly_ok:.1%}")

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    print(f"  Model saved → {MODEL_OUT}")

    meta = {
        "type": "IsolationForest",
        "feature_dim": 30,
        "contamination": 0.05,
        "output": "1 = normal, -1 = anomaly",
    }
    meta_path = MODEL_OUT.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved → {meta_path}")
    print("  Done ✓")


if __name__ == "__main__":
    train()
