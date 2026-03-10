#!/usr/bin/env python3
"""
Industrial Wearable AI — Edge Gateway Main
BLE/simulator → buffer → pipeline → classifier → POST /api/events
"""
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add project root for imports when run as python -m edge.src.main
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

_edge_dir = Path(__file__).resolve().parent.parent
load_dotenv(_edge_dir / ".env")

from .api_client import accel_mag_from_sample, post_device_status, post_events_with_buffer, post_sensor_snapshot, start_sync_loop
from .ble_client import read_ble_stream
from .buffer import SampleBuffer
from .anomaly_detector import AnomalyDetector
from .classifier import load_model, predict_with_confidence
from .pipeline import process_window
from .risk_detector import RiskDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
_model_path = os.getenv("MODEL_PATH", "ml/models/activity_model.joblib")
MODEL_PATH = _project_root / _model_path if not os.path.isabs(_model_path) else Path(_model_path)
_fatigue_model = os.getenv("FATIGUE_MODEL_PATH", "ml/models/fatigue_model.joblib")
FATIGUE_MODEL_PATH = _project_root / _fatigue_model if not os.path.isabs(_fatigue_model) else Path(_fatigue_model)
_ergo_model = os.getenv("ERGO_MODEL_PATH", "ml/models/ergo_model.joblib")
ERGO_MODEL_PATH = _project_root / _ergo_model if not os.path.isabs(_ergo_model) else Path(_ergo_model)
_anomaly_model = os.getenv("ANOMALY_MODEL_PATH", "ml/models/anomaly_model.joblib")
ANOMALY_MODEL_PATH = _project_root / _anomaly_model if not os.path.isabs(_anomaly_model) else Path(_anomaly_model)
BLE_DEVICE_ID = os.getenv("BLE_DEVICE_ID", "").strip() or None
WINDOW_SECONDS = float(os.getenv("WINDOW_SECONDS", "3"))
OVERLAP = float(os.getenv("OVERLAP", "0.5"))
WORKER_ID = os.getenv("WORKER_ID", "W01")
SAMPLE_RATE = 25.0
BATCH_SIZE = 5
FLUSH_INTERVAL_SEC = 2.5  # Send batch to backend at least this often so dashboard updates quickly
SENSOR_INTERVAL_SEC = 2.5  # Send sensor snapshot (temp, accel_mag) for live dashboard


from .health_server import start_health_server
from .ble_manager import BLEDeviceManager

def _run_edge():
    """Run edge pipeline: BLE stream → buffer → pipeline → classifier → API."""
    model = load_model(MODEL_PATH)
    if model:
        logger.info("Model loaded from %s", MODEL_PATH)
    else:
        logger.info("No model; using rule-based classifier")

    async def create_device_pipeline(mac_address: str | None, worker_id: str):
        logger.info("Initializing pipeline for worker %s (mac=%s)", worker_id, mac_address)
        
        risk_detector = RiskDetector(
            fatigue_model_path=FATIGUE_MODEL_PATH,
            ergo_model_path=ERGO_MODEL_PATH,
        )
        anomaly_detector = AnomalyDetector(model_path=ANOMALY_MODEL_PATH)

        buffer = SampleBuffer(max_seconds=WINDOW_SECONDS * 2, sample_rate=SAMPLE_RATE)
        window_samples = int(WINDOW_SECONDS * SAMPLE_RATE)
        step = max(1, int(window_samples * (1 - OVERLAP)))

        event_batch: list = []
        last_ts = 0
        samples_total = 0
        last_process_sample = 0
        last_sample: dict = {}  # latest raw sample for sensor snapshot
        first_sample_logged = False

        async def _on_sample(sample: dict):
            nonlocal last_ts, samples_total, last_process_sample, first_sample_logged
            if sample.get("mpu_connected") is False:
                await post_device_status(worker_id, False)
                return
            await post_device_status(worker_id, True)
            if not first_sample_logged:
                first_sample_logged = True
                logger.info("[%s] First BLE sample received; building buffer...", worker_id)
            
            last_sample.update(sample)
            buffer.append(sample)
            samples_total += 1
            win = buffer.get_window(window_samples)
            if win is None:
                return
            if samples_total - last_process_sample < step:
                return
            
            last_process_sample = samples_total
            features = process_window(win)
            label, confidence = predict_with_confidence(model, features)
            ts = int(time.time() * 1000)
            if ts <= last_ts:
                ts = last_ts + 100
            last_ts = ts

            risk_detector.update_rolling_state(label, interval_sec=WINDOW_SECONDS)
            fatigue_level, fatigue_score = risk_detector.detect_fatigue(features)
            ergo_level, ergo_score = risk_detector.detect_ergo_risk(features)
            is_anomaly, anomaly_score = anomaly_detector.detect(features)

            risk_ergo = ergo_level in ("medium", "high")
            risk_fatigue = fatigue_level in ("mild", "high")
            event_batch.append({
                "ts": ts,
                "label": label,
                "risk_ergo": risk_ergo,
                "risk_fatigue": risk_fatigue,
            })
            if len(event_batch) >= BATCH_SIZE:
                to_send = event_batch[:]
                event_batch.clear()
                await post_events_with_buffer(worker_id, to_send)

        async def _periodic_flush():
            while True:
                await asyncio.sleep(FLUSH_INTERVAL_SEC)
                if not event_batch:
                    continue
                to_send = event_batch[:]
                event_batch.clear()
                await post_events_with_buffer(worker_id, to_send)

        async def _periodic_sensor():
            while True:
                await asyncio.sleep(SENSOR_INTERVAL_SEC)
                if not last_sample:
                    continue
                temp = last_sample.get("temp")
                accel_mag = accel_mag_from_sample(last_sample)
                ts = last_sample.get("ts") or int(time.time() * 1000)
                await post_sensor_snapshot(worker_id, temp=temp, accel_mag=accel_mag, ts=ts)

        flush_task = asyncio.create_task(_periodic_flush())
        sensor_task = asyncio.create_task(_periodic_sensor())
        try:
            await read_ble_stream(
                mac_address,
                _on_sample,
                worker_id=worker_id,
                use_simulator=not mac_address,
            )
        except Exception as e:
            logger.error("[%s] Pipeline error: %s", worker_id, e)
        finally:
            flush_task.cancel()
            sensor_task.cancel()
            if event_batch:
                await post_events(worker_id, event_batch)

    async def _run():
        devices_file = _edge_dir / "devices.json"
        
        # Start offline buffer sync loop
        sync_task = asyncio.create_task(start_sync_loop())
        
        # Start edge health server on port 8081
        health_task = asyncio.create_task(start_health_server(port=8081))
        
        # If BLE_DEVICE_ID is provided via ENV, it overrides devices.json with a single deployment
        if BLE_DEVICE_ID:
            logger.info("Using ENV BLE_DEVICE_ID %s for worker %s", BLE_DEVICE_ID, WORKER_ID)
            await create_device_pipeline(BLE_DEVICE_ID, WORKER_ID)
        else:
            manager = BLEDeviceManager(str(devices_file), create_device_pipeline)
            try:
                await manager.start_all()
            except asyncio.CancelledError:
                manager.cancel_all()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Edge stopped")

if __name__ == "__main__":
    _run_edge()
