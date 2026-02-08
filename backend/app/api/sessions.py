"""
Industrial Wearable AI — Sessions API
GET /api/sessions, GET /api/sessions/{session_id}/summary
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Session, SessionAggregate, Worker
from app.schemas import SessionOut, SessionSummaryOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["sessions"])


@router.get("/sessions", response_model=list[SessionOut])
async def get_sessions(db: AsyncSession = Depends(get_db)):
    """Return sessions ordered by started_at desc, limit 50."""
    stmt = (
        select(Session)
        .options(selectinload(Session.worker))
        .order_by(Session.started_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().unique().all()
    return [
        SessionOut(
            id=s.id,
            worker_id=s.worker_id,
            worker_name=s.worker.name if s.worker else None,
            started_at=s.started_at,
            ended_at=s.ended_at,
            shift_label=s.shift_label,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/summary", response_model=SessionSummaryOut)
async def get_session_summary(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return session aggregate summary; 404 if not found."""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    agg = await db.get(SessionAggregate, session_id)
    worker = await db.get(Worker, session.worker_id)

    return SessionSummaryOut(
        session_id=session.id,
        worker_id=worker.name if worker else str(session.worker_id),
        active_pct=agg.active_pct if agg else None,
        idle_pct=agg.idle_pct if agg else None,
        adjusting_pct=agg.adjusting_pct if agg else None,
        error_pct=agg.error_pct if agg else None,
        alert_count=agg.alert_count if agg else 0,
    )
