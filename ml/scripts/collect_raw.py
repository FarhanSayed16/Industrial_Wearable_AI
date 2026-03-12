#!/usr/bin/env python3
"""
Industrial Wearable AI — Raw Data Collector
Writes CSV to ml/data/raw/ with columns: timestamp, ax, ay, az, gx, gy, gz, temp.
Data source: BLE/simulator or generate dummy for testing.
"""
import argparse
import asyncio
import csv
import os
import random
import sys
import time
from pathlib import Path

# Project root
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
COLUMNS = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "temp"]


def _make_dummy_sample() -> dict:
    """Generate one dummy sample for testing."""
    return {
        "timestamp": int(time.time() * 1000),
        "ax": round(random.uniform(-1, 1), 2),
        "ay": round(random.uniform(-1, 1), 2),
        "az": round(random.uniform(9, 10), 2),
        "gx": round(random.uniform(-50, 50), 1),
        "gy": round(random.uniform(-50, 50), 1),
        "gz": round(random.uniform(-50, 50), 1),
        "temp": round(random.uniform(28, 35), 1),
    }


def _sample_to_row(sample: dict) -> list:
    """Convert sample dict to CSV row. Handles both ts and timestamp."""
    ts = sample.get("timestamp") or sample.get("ts", 0)
    return [
        ts,
        sample.get("ax", 0),
        sample.get("ay", 0),
        sample.get("az", 0),
        sample.get("gx", 0),
        sample.get("gy", 0),
        sample.get("gz", 0),
        sample.get("temp", 0),
    ]


async def _collect_from_stream(duration_sec: float, output_path: Path, use_simulator: bool = True):
    """Collect from edge BLE stream (simulator or real)."""
    from edge.src.ble_client import stream_samples

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        count = 0
        async for s in stream_samples(use_simulator=use_simulator, duration_sec=duration_sec):
            row = _sample_to_row({**s, "timestamp": s.get("ts", 0)})
            writer.writerow(row)
            count += 1
    return count


def collect_dummy(duration_sec: float, sample_rate: float = 25) -> Path:
    """Generate dummy CSV for testing. Returns output path."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_path = RAW_DIR / f"raw_{ts}.csv"
    interval = 1.0 / sample_rate
    num_samples = int(duration_sec * sample_rate)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for _ in range(num_samples):
            row = _sample_to_row(_make_dummy_sample())
            writer.writerow(row)
            time.sleep(interval)

    return output_path


def main():
    p = argparse.ArgumentParser(description="Collect raw IMU data to CSV")
    p.add_argument("--duration", type=float, default=10, help="Duration in seconds")
    p.add_argument("--source", choices=["dummy", "stream"], default="dummy",
                   help="dummy=generate, stream=from edge BLE/simulator")
    p.add_argument("--output", help="Output path (default: raw_YYYYMMDD_HHMMSS.csv)")
    args = p.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output) if args.output else RAW_DIR / f"raw_{ts}.csv"

    if args.source == "dummy":
        path = collect_dummy(args.duration)
        print(f"Wrote {path} ({int(args.duration * 25)} samples)")
    else:
        count = asyncio.run(_collect_from_stream(args.duration, output_path))
        print(f"Wrote {output_path} ({count} samples)")


if __name__ == "__main__":
    main()
