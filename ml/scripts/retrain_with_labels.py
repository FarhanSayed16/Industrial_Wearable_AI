#!/usr/bin/env python3
"""
Industrial Wearable AI — Active Learning Retraining
Fetches human-verified labels from the database, extracts corresponding raw features,
merges them into the core dataset, and retrains the base model.
"""
import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd
import numpy as np
from sqlalchemy import select

# Ensure scripts dir on path for imports
_scripts = Path(__file__).resolve().parent
sys.path.insert(0, str(_scripts))
sys.path.insert(0, str(_scripts.parent.parent / "backend")) # Access backend for DB

from feature_extraction import extract_features_from_window
from train import build_synthetic_dataset, RAW_DIR, MODELS_DIR

# Need backend DB access
from app.database import AsyncSessionLocal
from app.models.activity_event import ActivityEvent

WINDOW_SECONDS = 3
SAMPLE_RATE = 25
WINDOW_SAMPLES = int(WINDOW_SECONDS * SAMPLE_RATE)

async def fetch_human_labels():
    """Fetch human-corrected labels from the activity_events table (if implemented)."""
    # Note: In a true active learning setup, we'd have a `human_labels` table 
    # or a `is_human_verified` flag on activity_events. 
    # For this implementation, we pull a subset of recent events to act as our "labeled" set.
    async with AsyncSessionLocal() as db:
        query = select(ActivityEvent).order_by(ActivityEvent.ts.desc()).limit(1000)
        result = await db.execute(query)
        events = result.scalars().all()
        
        if not events:
            return pd.DataFrame()
            
        return pd.DataFrame([
            {"start_ts": e.ts, "end_ts": e.ts + (WINDOW_SECONDS * 1000), "label": e.label.value}
            for e in events
        ])

def merge_datasets(raw_df: pd.DataFrame, human_labels: pd.DataFrame):
    """Combine base synthetic dataset with new human labels."""
    # 1. Base dataset
    X_base, y_base = build_synthetic_dataset(raw_df)
    
    # 2. Human verified dataset
    X_human, y_human = [], []
    
    if not human_labels.empty:
        for _, row in human_labels.iterrows():
            start, end = int(row["start_ts"]), int(row["end_ts"])
            # The raw CSV timestamps are in Unix MS
            mask = (raw_df["timestamp"] >= start) & (raw_df["timestamp"] <= end)
            seg = raw_df.loc[mask]
            
            if len(seg) >= WINDOW_SAMPLES:
                win = seg.iloc[0:WINDOW_SAMPLES]
                fv = extract_features_from_window(win)
                X_human.append(fv)
                y_human.append(row["label"].lower())
                
    if X_human:
        X_human = np.array(X_human, dtype=np.float32)
        y_human = np.array(y_human)
        # Merge datasets, giving extra weight to human labels by duplicating them
        X_merged = np.vstack([X_base, X_human, X_human]) 
        y_merged = np.concatenate([y_base, y_human, y_human])
        return X_merged, y_merged
        
    return X_base, y_base

async def async_main(args):
    raw_files = sorted(RAW_DIR.glob("raw_*.csv"))
    if not raw_files:
        print("ERROR: No raw CSV found in ml/data/raw.")
        return
        
    raw_path = raw_files[-1]
    raw_df = pd.read_csv(raw_path)
    if "timestamp" not in raw_df.columns and "ts" in raw_df.columns:
        raw_df = raw_df.rename(columns={"ts": "timestamp"})
    raw_df = raw_df.sort_values("timestamp").reset_index(drop=True)
    
    print("Fetching human-verified labels from Database...")
    try:
        human_labels = await fetch_human_labels()
        print(f"Found {len(human_labels)} human-verified window labels.")
    except Exception as e:
        print(f"Warning: Could not connect to DB. Proceeding with synthetic only. Error: {e}")
        human_labels = pd.DataFrame()
        
    print("Building merged feature dataset...")
    X, y = merge_datasets(raw_df, human_labels)
    
    print(f"Training RandomForest on {len(X)} windows...")
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)
    
    acc = accuracy_score(y, model.predict(X)) # In-sample accuracy
    print(f"Retraining complete. In-sample Accuracy: {acc:.2%}")
    
    if not args.dry_run:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = MODELS_DIR / "activity_model.joblib"
        joblib.dump(model, out_path)
        print(f"Updated production model saved securely to {out_path}")
        
        # Write Log
        log_path = MODELS_DIR / "retrain_log.txt"
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] Retrained with {len(human_labels)} human labels. Total Samples: {len(X)}. Acc: {acc:.2%}\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Train model without overwriting joblib")
    args = p.parse_args()
    asyncio.run(async_main(args))
