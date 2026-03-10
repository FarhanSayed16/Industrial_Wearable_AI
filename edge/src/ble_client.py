"""
Industrial Wearable AI — BLE Client & Simulator
read_ble_stream: real BLE or simulated samples. Sample format per TECHNICAL_STACK_SPEC §4.1.
"""
import asyncio
import json
import logging
import random
import time
from typing import Any, AsyncIterator, Callable, Optional

log = logging.getLogger(__name__)

# Bleak for real BLE (optional import)
try:
    from bleak import BleakClient, BleakScanner
    HAS_BLEAK = True
except ImportError:
    BleakScanner = None
    HAS_BLEAK = False

SAMPLE_RATE_HZ = 25
SAMPLE_INTERVAL = 1.0 / SAMPLE_RATE_HZ  # ~0.04 s


def _make_sim_sample(worker_id: str) -> dict:
    """Generate one fake sample matching §4.1 format."""
    return {
        "worker_id": worker_id,
        "ts": int(time.time() * 1000),
        "ax": round(random.uniform(-1, 1), 2),
        "ay": round(random.uniform(-1, 1), 2),
        "az": round(random.uniform(9, 10), 2),
        "gx": round(random.uniform(-50, 50), 1),
        "gy": round(random.uniform(-50, 50), 1),
        "gz": round(random.uniform(-50, 50), 1),
        "temp": round(random.uniform(28, 35), 1),
    }


async def _simulator_loop(
    worker_id: str,
    callback: Callable[[dict], Any],
) -> None:
    """Emit simulated samples at ~25 Hz. Runs until task cancelled."""
    while True:
        sample = _make_sim_sample(worker_id)
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(sample)
            else:
                callback(sample)
        except Exception:
            pass
        await asyncio.sleep(SAMPLE_INTERVAL)


async def read_ble_stream(
    device_id: Optional[str],
    callback: Callable[[dict], Any],
    worker_id: str = "W01",
    use_simulator: Optional[bool] = None,
) -> None:
    """
    Async stream of raw samples. If use_simulator or no device_id: generate fake samples.
    Otherwise connect to BLE device and read GATT characteristic.
    Runs until task is cancelled.
    """
    if use_simulator is None:
        use_simulator = not device_id

    if use_simulator or not device_id:
        await _simulator_loop(worker_id, callback)
        return

    # Real BLE mode (when firmware is ready)
    if not HAS_BLEAK:
        raise RuntimeError("bleak not installed; use simulator or pip install bleak")

    CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"  # Must match firmware

    async def _ble_notify_handler(sender, data: bytearray):
        try:
            text = data.decode("utf-8")
            sample = json.loads(text)
            if asyncio.iscoroutinefunction(callback):
                await callback(sample)
            else:
                callback(sample)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    BLE_NAME = "WearableAI"
    scan_timeout = 10.0
    max_retries = 5

    for attempt in range(max_retries):
        address = device_id
        # On Windows, device is often "not found" until we scan first
        if BleakScanner is not None:
            log.info("Scanning for BLE device (attempt %s/%s)...", attempt + 1, max_retries)
            try:
                device = await BleakScanner.find_device_by_address(device_id, timeout=scan_timeout)
                if device is None:
                    devices = await BleakScanner.discover(timeout=scan_timeout)
                    device = next(
                        (d for d in devices if d.name and BLE_NAME in d.name),
                        next((d for d in devices if d.address and d.address.upper().replace("-", ":") == device_id.upper().replace("-", ":")), None),
                    )
                if device is not None:
                    address = device.address
                    log.info("Device found at %s, connecting (timeout=60s)...", address)
                else:
                    raise RuntimeError(
                        f"'{BLE_NAME}' not found. Is the ESP32 powered and advertising? "
                        "Keep it close to the laptop and try again."
                    )
            except RuntimeError:
                raise
            except Exception as e:
                log.warning("Scan failed: %s", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2.0 * (attempt + 1))
                    continue
                raise RuntimeError(
                    f"Could not find BLE device. Is the ESP32 on and advertising as '{BLE_NAME}'?"
                ) from e

        # Longer timeout for BLE connect (Windows can be slow)
        client = BleakClient(address, timeout=60.0)
        try:
            await client.connect()
            if not client.is_connected:
                raise RuntimeError("BLE connect failed")
            await asyncio.sleep(0.3)
            await client.start_notify(CHAR_UUID, _ble_notify_handler)
            log.info("BLE connected and notify started for %s", address)
            try:
                while client.is_connected:
                    await asyncio.sleep(1)
            finally:
                await client.disconnect()
        except Exception as e:
            err_msg = str(e).lower()
            if attempt < max_retries - 1 and (
                "not found" in err_msg or "not connected" in err_msg or "unreachable" in err_msg
                or "notify" in err_msg or "timeout" in err_msg
            ):
                log.warning("BLE attempt %s failed: %s; retrying...", attempt + 1, e)
                await asyncio.sleep(2.0 * (attempt + 1))
                continue
            if "unreachable" in err_msg or ("notify" in err_msg and "not connected" not in err_msg):
                raise RuntimeError(
                    "BLE notify failed (on Windows often when device is paired). "
                    "Unpair 'WearableAI' in Settings > Bluetooth > Devices, then run the edge again."
                ) from e
            raise
        finally:
            if client.is_connected:
                try:
                    await client.disconnect()
                except Exception:
                    pass


async def stream_samples(
    device_id: Optional[str] = None,
    worker_id: str = "W01",
    use_simulator: bool = True,
    duration_sec: Optional[float] = None,
) -> AsyncIterator[dict]:
    """
    Async generator yielding samples. Useful for pipeline consumption.
    """
    samples: list = []

    def _cb(s: dict):
        samples.append(s)

    async def _run():
        await read_ble_stream(device_id, _cb, worker_id, use_simulator)

    task = asyncio.create_task(_run())
    try:
        start = time.time()
        while True:
            if duration_sec and (time.time() - start) >= duration_sec:
                break
            while samples:
                yield samples.pop(0)
            await asyncio.sleep(0.01)
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
