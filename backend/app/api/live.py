"""
Industrial Wearable AI — Live API
POST /api/live/sensor — accept sensor snapshot from edge; broadcast to WebSocket clients.
POST /api/live/device-status — MPU connected or not; broadcast so dashboard can show "No MPU connected".
"""
import time
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import verify_edge_api_key
from app.services.websocket_hub import ws_hub

router = APIRouter(prefix="/api/live", tags=["live"])


class SensorSnapshot(BaseModel):
    """Payload from edge: temp and movement (accel magnitude) for live dashboard."""
    worker_id: str
    ts: int
    temp: Optional[float] = None
    accel_mag: Optional[float] = None


@router.post("/sensor", dependencies=[Depends(verify_edge_api_key)])
async def post_sensor(snapshot: SensorSnapshot):
    """
    Accept sensor snapshot from edge (temp, accel_mag). Broadcast to WebSocket clients
    so the dashboard can show live temp and movement per worker.
    """
    msg = {
        "type": "sensor",
        "worker_id": snapshot.worker_id,
        "ts": snapshot.ts,
    }
    if snapshot.temp is not None:
        msg["temp"] = snapshot.temp
    if snapshot.accel_mag is not None:
        msg["accel_mag"] = snapshot.accel_mag
    await ws_hub.broadcast(msg)
    return {"status": "ok"}


class DeviceStatus(BaseModel):
    """Device reports MPU connected or not; no fake IMU data when disconnected."""
    worker_id: str
    mpu_connected: bool


@router.post("/device-status", dependencies=[Depends(verify_edge_api_key)])
async def post_device_status(status: DeviceStatus):
    """
    Edge posts when device reports mpu_connected true/false.
    Broadcast so dashboard can show "No MPU connected" without showing fake data.
    When MPU not connected, also broadcast a minimal worker state so the worker appears on the dashboard.
    """
    await ws_hub.broadcast({
        "type": "device_status",
        "worker_id": status.worker_id,
        "mpu_connected": status.mpu_connected,
    })
    if not status.mpu_connected:
        now_ms = int(time.time() * 1000)
        await ws_hub.broadcast({
            "worker_id": status.worker_id,
            "name": status.worker_id,
            "current_state": "idle",
            "risk_ergo": False,
            "risk_fatigue": False,
            "updated_at": now_ms,
        })
    return {"status": "ok"}
