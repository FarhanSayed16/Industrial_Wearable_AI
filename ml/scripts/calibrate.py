#!/usr/bin/env python3
"""
Industrial Wearable AI — Per-Factory Calibration
Loads the global base activity model, takes a tiny sample of local factory data (e.g. 1-2 hours),
and fine-tunes the tree estimators using the local mechanical variance directly on the edge gateway.
"""
import sys
import argparse
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

# Ensure scripts dir on path for imports
_scripts = Path(__file__).resolve().parent
sys.path.insert(0, str(_scripts))

from feature_extraction import extract_features_from_window
from train import build_dataset, load_labels, MODELS_DIR

WINDOW_SECONDS = 3
SAMPLE_RATE = 25
WINDOW_SAMPLES = int(WINDOW_SECONDS * SAMPLE_RATE)

def main():
    p = argparse.ArgumentParser(description="Calibrate activity model per factory")
    p.add_argument("--factory-id", type=str, required=True, help="Factory identifier (e.g., F001)")
    p.add_argument("--local-raw", type=Path, required=True, help="Path to the factory's raw CSV file")
    p.add_argument("--local-labels", type=Path, required=True, help="Path to the factory's labels CSV file")
    args = p.parse_args()

    # Load 
    base_model_path = MODELS_DIR / "activity_model.joblib"
    if not base_model_path.exists():
        print(f"Error: Base model {base_model_path.name} not found. Train first.")
        return 1
        
    print(f"[1/4] Loading global base model: {base_model_path.name}")
    base_model = joblib.load(base_model_path)
    
    print(f"[2/4] Loading local factory data: {args.local_raw.name}")
    raw_df = pd.read_csv(args.local_raw)
    if "timestamp" not in raw_df.columns and "ts" in raw_df.columns:
        raw_df = raw_df.rename(columns={"ts": "timestamp"})
    raw_df = raw_df.sort_values("timestamp").reset_index(drop=True)
    
    labels_df = load_labels(args.local_labels)
    X_local, y_local = build_dataset(raw_df, labels_df)
    
    if len(X_local) < 5:
        print("Error: Supplied local dataset is too small. Need at least 5 windows.")
        return 1
        
    print(f"[3/4] Fine-tuning baseline with {len(X_local)} local windows...")
    # NOTE: Scikit-learn Random Forests do not technically support "online warm-start" easily on new classes
    # But we can increase `n_estimators` using `warm_start=True` to append local variance trees.
    
    base_model.warm_start = True
    base_model.n_estimators += 25 # Add 25 new trees catered specifically to local data
    
    # Train the newly appended trees strictly on the new local dataset
    base_model.fit(X_local, y_local)
    
    print(f"[4/4] Evaluating local calibration...")
    from sklearn.metrics import accuracy_score
    y_pred = base_model.predict(X_local)
    local_acc = accuracy_score(y_local, y_pred)
    print(f"Local Calibration Accuracy: {local_acc:.2%}")
    
    # Export customized factory profile
    out_path = MODELS_DIR / f"activity_factory_{args.factory_id}.joblib"
    joblib.dump(base_model, out_path)
    print(f"\n✅ Factory model exported: {out_path.name}")
    
if __name__ == "__main__":
    exit(main())
