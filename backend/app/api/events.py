"""
Industrial Wearable AI — Events API
POST /api/events — accept EventBatch, resolve/create worker & session, insert events.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_edge_api_key
from app.models import ActivityEvent, ActivityLabel, Session, Worker
from app.schemas import EventBatch
from app.services.event_service import update_session_aggregate
from app.services.websocket_hub import ws_hub

router = APIRouter(prefix="/api", tags=["events"])


def _ts_to_datetime(ts_ms: int) -> datetime:
    """Convert Unix ms to timezone-aware datetime."""
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)


def _label_from_str(s: str) -> ActivityLabel:
    """Map API label string to ActivityLabel enum."""
    try:
        return ActivityLabel(s.lower())
    except ValueError:
        return ActivityLabel.IDLE  # fallback


@router.post("/events", dependencies=[Depends(verify_edge_api_key)])
async def post_events(batch: EventBatch, db: AsyncSession = Depends(get_db)):
    """
    Accept EventBatch from edge. Resolve or create Worker (by name=worker_id for MVP).
    Resolve or create active Session. Insert events. Update aggregates.
    """
    # Resolve or create Worker (MVP: worker_id becomes name)
    stmt = select(Worker).where(Worker.name == batch.worker_id)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if not worker:
        worker = Worker(name=batch.worker_id, role=None)
        db.add(worker)
        await db.flush()

    # Resolve or create active Session (no ended_at)
    stmt = (
        select(Session)
        .where(Session.worker_id == worker.id)
        .where(Session.ended_at.is_(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        # Create new session — started_at = first event ts
        first_ts = batch.events[0].ts
        session = Session(
            worker_id=worker.id,
            started_at=_ts_to_datetime(first_ts),
        )
        db.add(session)
        await db.flush()

    # Insert events
    for ev in batch.events:
        activity = ActivityEvent(
            session_id=session.id,
            ts=_ts_to_datetime(ev.ts),
            label=_label_from_str(ev.label),
            risk_ergo=ev.risk_ergo,
            risk_fatigue=ev.risk_fatigue,
        )
        db.add(activity)

    await db.flush()
    await update_session_aggregate(db, session.id)

    # Broadcast live state to WebSocket clients (per TECHNICAL_STACK_SPEC §4.3)
    last_ev = batch.events[-1]
    await ws_hub.broadcast({
        "worker_id": batch.worker_id,
        "name": worker.name,
        "current_state": last_ev.label,
        "risk_ergo": last_ev.risk_ergo,
        "risk_fatigue": last_ev.risk_fatigue,
        "updated_at": last_ev.ts,
    })

    return {"status": "ok", "count": len(batch.events)}
