#!/usr/bin/env python3
"""
Industrial Wearable AI — Training Script
Load raw + labels, extract features, train RandomForestClassifier, export joblib.
"""
import argparse
import sys
from pathlib import Path

# Ensure scripts dir on path for imports
_scripts = Path(__file__).resolve().parent
sys.path.insert(0, str(_scripts))
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from feature_extraction import extract_features_from_window

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
LABELED_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
LABELS = ["sewing", "idle", "adjusting", "error", "break"]
WINDOW_SECONDS = 3
SAMPLE_RATE = 25
WINDOW_SAMPLES = int(WINDOW_SECONDS * SAMPLE_RATE)


def load_raw(path: Path) -> pd.DataFrame:
    """Load raw CSV with timestamp, ax, ay, az, gx, gy, gz, temp."""
    df = pd.read_csv(path)
    if "timestamp" not in df.columns and "ts" in df.columns:
        df = df.rename(columns={"ts": "timestamp"})
    return df.sort_values("timestamp").reset_index(drop=True)


def load_labels(path: Path) -> pd.DataFrame:
    """Load labels CSV with start_ts, end_ts, label."""
    return pd.read_csv(path)


def build_dataset(raw_df: pd.DataFrame, labels_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extract features per labeled segment. Return X, y."""
    X_list, y_list = [], []
    for _, row in labels_df.iterrows():
        start, end = int(row["start_ts"]), int(row["end_ts"])
        mask = (raw_df["timestamp"] >= start) & (raw_df["timestamp"] <= end)
        seg = raw_df.loc[mask]
        if len(seg) < WINDOW_SAMPLES:
            continue
        # Sliding windows within segment (50% overlap)
        step = max(1, WINDOW_SAMPLES // 2)
        for i in range(0, len(seg) - WINDOW_SAMPLES + 1, step):
            win = seg.iloc[i : i + WINDOW_SAMPLES]
            fv = extract_features_from_window(win)
            X_list.append(fv)
            y_list.append(row["label"].lower())
    return np.array(X_list, dtype=np.float32), np.array(y_list)


def build_synthetic_dataset(raw_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Build dataset with synthetic labels (for testing without real labels)."""
    X_list, y_list = [], []
    step = max(1, WINDOW_SAMPLES // 4)  # Smaller step for more synthetic samples
    for i in range(0, len(raw_df) - WINDOW_SAMPLES + 1, step):
        win = raw_df.iloc[i : i + WINDOW_SAMPLES]
        fv = extract_features_from_window(win)
        X_list.append(fv)
        # Assign label by variance (simple heuristic)
        var_sum = np.sum(fv[[1, 6, 11, 16, 21, 26]])
        if var_sum < 0.5:
            lbl = "idle"
        elif var_sum < 2.0:
            lbl = "adjusting"
        else:
            lbl = "sewing"
        y_list.append(lbl)
    return np.array(X_list, dtype=np.float32), np.array(y_list)


def main():
    p = argparse.ArgumentParser(description="Train activity classifier")
    p.add_argument("--raw", type=Path, help="Raw CSV path (default: latest in ml/data/raw)")
    p.add_argument("--labels", type=Path, help="Labels CSV path")
    p.add_argument("--synthetic", action="store_true", help="Use synthetic labels (no labels file)")
    p.add_argument("--output", type=Path, help="Output model path (default: ml/models/activity_model.joblib)")
    p.add_argument("--test-size", type=float, default=0.2, help="Validation fraction")
    args = p.parse_args()

    raw_path = args.raw
    if not raw_path:
        raw_files = sorted(RAW_DIR.glob("raw_*.csv"))
        if not raw_files:
            print("ERROR: No raw CSV found. Run collect_raw.py first.")
            return 1
        raw_path = raw_files[-1]
    raw_df = load_raw(raw_path)
    print(f"Raw: {raw_path.name}, {len(raw_df)} rows")

    if args.synthetic or not args.labels:
        X, y = build_synthetic_dataset(raw_df)
        print(f"Synthetic labels: {len(X)} windows")
    else:
        labels_df = load_labels(args.labels)
        X, y = build_dataset(raw_df, labels_df)
        print(f"Labels: {args.labels.name}, {len(X)} windows")

    if len(X) < 10:
        print("ERROR: Too few samples. Need at least 10 windows.")
        return 1

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"\nAccuracy: {acc:.2%}")
    print(classification_report(y_val, y_pred, zero_division=0))

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.output or MODELS_DIR / "activity_model.joblib"
    joblib.dump(model, out_path)
    print(f"Model saved: {out_path}")

    # Write MODEL_CARD
    card_path = MODELS_DIR / "MODEL_CARD.md"
    card_path.write_text(f"""# Activity Model Card

## Training
- **Date:** {datetime.now().isoformat()}
- **Raw data:** {raw_path.name}
- **Labels:** {"synthetic" if args.synthetic else str(args.labels)}
- **Samples:** {len(X)} windows

## Parameters
- **Window:** {WINDOW_SECONDS}s ({WINDOW_SAMPLES} samples @ {SAMPLE_RATE} Hz)
- **Overlap:** 50%
- **Model:** RandomForestClassifier (n_estimators=100, max_depth=10)

## Features (30)
Per axis (ax,ay,az,gx,gy,gz): mean, std, min, max, zero_crossing_rate

## Metrics
- **Accuracy:** {acc:.2%}
""", encoding="utf-8")
    print(f"Model card: {card_path}")

    return 0 if acc >= 0.85 else 1


if __name__ == "__main__":
    exit(main())
