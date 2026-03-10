"""
Industrial Wearable AI — Backend API Client
POST events to backend. Payload per TECHNICAL_STACK_SPEC §4.2.
POST sensor snapshot for live temp/movement (Phase C).
"""
import math
import os
import time
from typing import List, Optional

import aiohttp
import logging
from dotenv import load_dotenv

from .offline_buffer import edge_buffer

load_dotenv()

log = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
EDGE_API_KEY = os.getenv("EDGE_API_KEY", "dev-edge-key-123")
API_HEADERS = {"X-API-Key": EDGE_API_KEY}


def accel_mag_from_sample(sample: dict) -> float:
    """Compute magnitude of acceleration (ax, ay, az) in g."""
    ax = float(sample.get("ax") or 0)
    ay = float(sample.get("ay") or 0)
    az = float(sample.get("az") or 0)
    return round(math.sqrt(ax * ax + ay * ay + az * az), 2)


async def post_events(
    worker_id: str,
    events: List[dict],
) -> bool:
    """
    POST to BACKEND_URL/api/events.
    events: [{ts, label, risk_ergo, risk_fatigue}]
    Return True if status 200.
    """
    if not events:
        return True
    url = f"{BACKEND_URL.rstrip('/')}/api/events"
    payload = {"worker_id": worker_id, "events": events}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=API_HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                return resp.status == 200
    except Exception:
        return False

async def post_events_with_buffer(worker_id: str, events: List[dict]) -> bool:
    """
    Tries to POST events. If fails, stores in local SQLite buffer.
    Always returns True so caller can clear its memory batch.
    """
    if not events:
        return True
    ok = await post_events(worker_id, events)
    if not ok:
        log.warning("[%s] Backend unreachable; queueing %d events to offline buffer", worker_id, len(events))
        await edge_buffer.add_events(worker_id, events)
    return True

async def start_sync_loop():
    """Background task to push buffered events when backend is up."""
    while True:
        await asyncio.sleep(5.0)
        count = await edge_buffer.get_count()
        if count == 0:
            continue
            
        # Try a ping first
        url = f"{BACKEND_URL.rstrip('/')}/health"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as resp:
                    if resp.status != 200:
                        continue
        except Exception:
            continue
            
        log.info("Backend reachable. Syncing offline buffer (%d batches pending)...", count)
        batches = await edge_buffer.get_batch(limit=10)
        success_ids = []
        
        for record_id, worker_id, payload in batches:
            ok = await post_events(worker_id, payload)
            if ok:
                success_ids.append(record_id)
            else:
                break # Stop if it fails mid-sync
                
        if success_ids:
            await edge_buffer.delete_batch(success_ids)
            log.info("Successfully synced %d batches to backend.", len(success_ids))


async def post_sensor_snapshot(
    worker_id: str,
    temp: Optional[float] = None,
    accel_mag: Optional[float] = None,
    ts: Optional[int] = None,
) -> bool:
    """
    POST to BACKEND_URL/api/live/sensor for live dashboard (temp, movement).
    Backend broadcasts to WebSocket clients with type "sensor".
    """
    url = f"{BACKEND_URL.rstrip('/')}/api/live/sensor"
    payload = {
        "worker_id": worker_id,
        "ts": ts or int(time.time() * 1000),
    }
    if temp is not None:
        payload["temp"] = round(float(temp), 1)
    if accel_mag is not None:
        payload["accel_mag"] = round(float(accel_mag), 2)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=API_HEADERS, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
    except Exception:
        return False


async def post_device_status(worker_id: str, mpu_connected: bool) -> bool:
    """
    POST to BACKEND_URL/api/live/device-status when device reports MPU connected or not.
    Dashboard uses this to show "No MPU connected" instead of fake data.
    """
    url = f"{BACKEND_URL.rstrip('/')}/api/live/device-status"
    payload = {"worker_id": worker_id, "mpu_connected": mpu_connected}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=API_HEADERS, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
    except Exception:
        return False
