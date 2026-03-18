#!/usr/bin/env python3
"""
Industrial Wearable AI — Data Simulator
POSTs mock activity events to backend for testing without hardware.

Usage:
    python simulator.py
    python simulator.py --worker W02 --duration 60 --interval 2
    BASE_URL=http://localhost:8000 python simulator.py

Env / CLI:
    BASE_URL      — Backend URL (default: http://localhost:8000)
    worker_id     — Worker ID (default: W01)
    duration_sec  — Run duration in seconds (default: 30)
    interval_sec  — Seconds between batches (default: 1)
"""
import argparse
import os
import random
import sys
import time
from pathlib import Path

# Add project root for imports if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

LABELS = ["sewing", "idle", "adjusting", "error", "break"]


def parse_args():
    p = argparse.ArgumentParser(description="Simulate activity events to backend")
    p.add_argument("--url", default=os.getenv("BASE_URL", "http://localhost:8000"), help="Backend base URL")
    p.add_argument("--worker", default=os.getenv("WORKER_ID", "W01"), help="Worker ID")
    p.add_argument("--duration", type=int, default=int(os.getenv("DURATION_SEC", "30")), help="Run duration (sec)")
    p.add_argument("--interval", type=float, default=float(os.getenv("INTERVAL_SEC", "1")), help="Interval between batches (sec)")
    return p.parse_args()


def make_event(ts_ms: int) -> dict:
    """Generate one event with random label. risk_fatigue when idle."""
    label = random.choice(LABELS)
    risk_ergo = False
    risk_fatigue = label == "idle" and random.random() < 0.3  # 30% when idle
    return {"ts": ts_ms, "label": label, "risk_ergo": risk_ergo, "risk_fatigue": risk_fatigue}


def run_simulator(url: str, worker_id: str, duration_sec: int, interval_sec: float):
    endpoint = f"{url.rstrip('/')}/api/events"
    start = time.time()
    batch_num = 0

    print(f"Simulator: {worker_id} -> {endpoint} for {duration_sec}s, interval={interval_sec}s")
    print("Press Ctrl+C to stop early.\n")

    while (time.time() - start) < duration_sec:
        batch_num += 1
        ts_ms = int(time.time() * 1000)
        events = [make_event(ts_ms + i * 100) for i in range(random.randint(1, 3))]

        payload = {"worker_id": worker_id, "events": events}

        try:
            r = requests.post(endpoint, json=payload, timeout=5)
            r.raise_for_status()
            print(f"  Batch {batch_num}: {len(events)} events -> {r.json().get('status', 'ok')}")
        except requests.RequestException as e:
            print(f"  Batch {batch_num}: ERROR {e}")

        time.sleep(interval_sec)

    print(f"\nDone. Sent {batch_num} batches.")


if __name__ == "__main__":
    args = parse_args()
    run_simulator(args.url, args.worker, args.duration, args.interval)
