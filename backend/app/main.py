"""
Industrial Wearable AI — FastAPI Application Entry Point
"""
import logging
import time

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, events, sessions, workers
from app.config import CORS_ORIGINS
from app.database import get_db
from app.services.websocket_hub import ws_hub

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industrial Wearable AI API",
    description="Backend API for wearable activity monitoring",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request path and status."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info("%s %s %s %.1fms", request.method, request.url.path, response.status_code, duration_ms)
    return response


# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(workers.router)
app.include_router(sessions.router)


@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/db-check")
async def db_check():
    """Verify database connection."""
    async for session in get_db():
        return {"status": "ok", "database": "connected"}


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket endpoint for live state broadcast to dashboard."""
    await ws_hub.connect(websocket)
    try:
        while True:
            # Keep connection alive; receive loop (discard client messages)
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        ws_hub.disconnect(websocket)


@app.get("/api/version")
async def version():
    """Service version (developer ergonomics)."""
    return {
        "service": "industrial-wearable-ai",
        "version": "0.1.0",
        "build_time": None,
    }
