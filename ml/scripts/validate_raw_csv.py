#!/usr/bin/env python3
"""
Industrial Wearable AI — Raw CSV Validation
Validates required columns, timestamps, NaNs. Exit non-zero on critical failure.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "temp"]


def validate(path: Path) -> bool:
    """Validate raw CSV. Return True if OK, False on critical failure."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"ERROR: Cannot read CSV: {e}")
        return False

    errors = []

    # Required columns
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Timestamp numeric and monotonic
    if "timestamp" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["timestamp"]):
            errors.append("timestamp must be numeric")
        else:
            diff = df["timestamp"].diff()
            non_mono = (diff < 0).sum()
            if non_mono > len(df) * 0.1:
                errors.append(f"timestamp: {non_mono} non-monotonic pairs (>10%)")

    # NaNs
    nan_counts = df.isna().sum()
    if nan_counts.any():
        bad = nan_counts[nan_counts > 0]
        if (bad / len(df) > 0.5).any():
            errors.append(f"Excessive NaNs: {bad[bad / len(df) > 0.5].to_dict()}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return False

    # Summary
    row_count = len(df)
    if "timestamp" in df.columns and row_count >= 2:
        span_ms = df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]
        span_sec = span_ms / 1000
        rate = row_count / span_sec if span_sec > 0 else 0
        print(f"Rows: {row_count}, Time span: {span_sec:.1f}s, Est. rate: {rate:.1f} Hz")
    else:
        print(f"Rows: {row_count}")

    return True


def main():
    p = argparse.ArgumentParser(description="Validate raw CSV")
    p.add_argument("file", type=Path, help="Path to raw CSV")
    args = p.parse_args()
    ok = validate(args.file)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
