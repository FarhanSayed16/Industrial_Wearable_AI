"""
Industrial Wearable AI — Workers API
GET /api/workers, GET /api/workers/{worker_name}/history
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Session, Worker
from app.schemas import WorkerOut, WorkerHistoryEntry
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["workers"])


@router.get("/workers", response_model=list[WorkerOut])
async def get_workers(db: AsyncSession = Depends(get_db)):
    """Return all workers."""
    stmt = select(Worker).order_by(Worker.name)
    result = await db.execute(stmt)
    workers = result.scalars().all()
    return workers


@router.get("/workers/{worker_name}/history", response_model=list[WorkerHistoryEntry])
async def get_worker_history(
    worker_name: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 30,
):
    """Return session history with aggregates for a worker (by name). For demo/historical view."""
    stmt = (
        select(Worker)
        .where(Worker.name == worker_name)
    )
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    stmt = (
        select(Session)
        .options(selectinload(Session.aggregate))
        .where(Session.worker_id == worker.id)
        .order_by(Session.started_at.desc())
        .limit(max(1, min(limit, 100)))
    )
    result = await db.execute(stmt)
    sessions = result.scalars().unique().all()

    return [
        WorkerHistoryEntry(
            session_id=s.id,
            started_at=s.started_at,
            ended_at=s.ended_at,
            active_pct=s.aggregate.active_pct if s.aggregate else None,
            idle_pct=s.aggregate.idle_pct if s.aggregate else None,
            adjusting_pct=s.aggregate.adjusting_pct if s.aggregate else None,
            error_pct=s.aggregate.error_pct if s.aggregate else None,
            alert_count=s.aggregate.alert_count if s.aggregate else 0,
        )
        for s in sessions
    ]
