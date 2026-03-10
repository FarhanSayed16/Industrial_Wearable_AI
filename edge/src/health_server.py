"""
Industrial Wearable AI — Edge Health Server
Exposes a lightweight local HTTP API to inspect edge gateway status.
"""
import aiohttp.web
import asyncio
import logging
import time
from .offline_buffer import edge_buffer

log = logging.getLogger(__name__)

# Track when the edge started
START_TIME = time.time()

async def health_handler(request):
    """Handle GET /status"""
    try:
        buffer_count = await edge_buffer.get_count()
        uptime = int(time.time() - START_TIME)
        
        data = {
            "status": "ok",
            "uptime_seconds": uptime,
            "buffer_depth_batches": buffer_count,
        }
        return aiohttp.web.json_response(data)
    except Exception as e:
        log.error("Health API error: %s", e)
        return aiohttp.web.json_response({"status": "error", "message": str(e)}, status=500)

async def start_health_server(host="0.0.0.0", port=8081):
    """Start the aiohttp web server concurrently with the BLE process."""
    app = aiohttp.web.Application()
    app.router.add_get("/status", health_handler)
    
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    
    log.info("Starting Edge Health API on http://%s:%d/status", host, port)
    await site.start()
    
    # Keep the task alive indefinitely
    while True:
        await asyncio.sleep(3600)
