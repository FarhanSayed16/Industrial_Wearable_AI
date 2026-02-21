"""
Industrial Wearable AI — Labels API (Active Learning)
POST /api/labels     — submit a human label for a low-confidence event
GET  /api/labels/queue — get events pending human review
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ActivityEvent, Session, Worker

router = APIRouter(prefix="/api/labels", tags=["labels"])

# In-memory store for labels (in production, use a DB table)
_label_store: list[dict] = []


class LabelSubmission(BaseModel):
    """Human-provided label for a low-confidence event."""
    event_id: str = Field(..., description="Activity event ID")
    human_label: str = Field(..., description="Corrected label: sewing|idle|adjusting|break|error")
    notes: str = ""


class LabelQueueItem(BaseModel):
    """An event pending human review."""
    event_id: str
    worker_name: str
    timestamp: str
    predicted_label: str
    confidence: float


@router.post("")
async def submit_label(label: LabelSubmission):
    """Submit a human-corrected label for an event."""
    _label_store.append({
        "event_id": label.event_id,
        "human_label": label.human_label,
        "notes": label.notes,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "ok", "total_labels": len(_label_store)}


@router.get("/queue")
async def get_label_queue(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent events for human labeling.
    In production, these would be filtered by confidence < 0.7.
    For now, returns the most recent events as candidates.
    """
    stmt = (
        select(
            ActivityEvent.id,
            ActivityEvent.label,
            ActivityEvent.ts,
            Worker.name.label("worker_name"),
        )
        .join(Session, Session.id == ActivityEvent.session_id)
        .join(Worker, Worker.id == Session.worker_id)
        .order_by(ActivityEvent.ts.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Filter out already-labeled events
    labeled_ids = {item["event_id"] for item in _label_store}

    return [
        LabelQueueItem(
            event_id=str(row.id),
            worker_name=row.worker_name,
            timestamp=row.ts.isoformat() if row.ts else "",
            predicted_label=row.label.value if hasattr(row.label, "value") else str(row.label),
            confidence=0.65,  # Placeholder — real confidence would be stored with the event
        )
        for row in rows
        if str(row.id) not in labeled_ids
    ]


@router.get("/submitted")
async def get_submitted_labels():
    """Get all human-submitted labels (for retraining)."""
    return _label_store
