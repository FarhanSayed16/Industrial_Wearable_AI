"""
Industrial Wearable AI — Multi-Device BLE Manager
Parses devices.json and runs concurrent device pipelines.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Callable, Coroutine

log = logging.getLogger(__name__)

class BLEDeviceManager:
    def __init__(self, config_path: str, pipeline_factory: Callable[[str | None, str], Coroutine]):
        self.config_path = Path(config_path)
        self.pipeline_factory = pipeline_factory
        self.tasks = []

    def load_devices(self) -> list[dict]:
        if not self.config_path.exists():
            log.warning("Config file %s not found, defaulting to single simulator.", self.config_path)
            return [{"mac_address": None, "worker_id": "W01"}]
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            log.error("Failed to load %s: %s", self.config_path, e)
            return [{"mac_address": None, "worker_id": "W01"}]

    async def start_all(self):
        devices = self.load_devices()
        log.info("Starting %d device pipelines...", len(devices))
        
        for d in devices:
            mac = d.get("mac_address")
            worker_id = d.get("worker_id", "Unknown")
            
            if mac and mac.startswith("SIMULATOR"):
                mac = None  # Force simulation mode for this device
                
            task = asyncio.create_task(self.pipeline_factory(mac, worker_id))
            self.tasks.append(task)
            
        # Run all devices concurrently
        await asyncio.gather(*self.tasks, return_exceptions=True)

    def cancel_all(self):
        for task in self.tasks:
            task.cancel()
