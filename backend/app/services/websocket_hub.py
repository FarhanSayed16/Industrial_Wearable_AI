"""
Industrial Wearable AI — WebSocket Connection Hub
Manages active connections and broadcasts live state to dashboard clients.
"""
import logging
from typing import List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketHub:
    """Connection manager for /ws/live broadcasts."""

    def __init__(self):
        self._connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept connection and add to list."""
        await websocket.accept()
        self._connections.append(websocket)
        logger.info("WebSocket connected; total=%d", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove from list."""
        if websocket in self._connections:
            self._connections.remove(websocket)
            logger.info("WebSocket disconnected; total=%d", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Send JSON to all connected clients."""
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning("Broadcast failed for client: %s", e)
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


# Singleton instance
ws_hub = WebSocketHub()
