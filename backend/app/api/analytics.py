"""
Industrial Wearable AI — Analytics API
GET /api/analytics/productivity  — daily active % per worker
GET /api/analytics/heatmap       — worker × hour-of-day activity grid
GET /api/analytics/ranking       — workers ranked by avg productivity
GET /api/analytics/state-breakdown — per-worker state distribution
"""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models import ActivityEvent, ActivityLabel, Session, SessionAggregate, Worker
from app.services.root_cause import generate_insights

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _default_range(from_ts: int | None, to_ts: int | None) -> tuple[datetime, datetime]:
    """Return (from_dt, to_dt), defaulting to last 7 days."""
    to_dt = (
        datetime.fromtimestamp(to_ts / 1000.0, tz=timezone.utc)
        if to_ts
        else datetime.now(timezone.utc)
    )
    from_dt = (
        datetime.fromtimestamp(from_ts / 1000.0, tz=timezone.utc)
        if from_ts
        else to_dt - timedelta(days=7)
    )
    return from_dt, to_dt


@router.get("/productivity")
async def get_productivity(
    from_ts: int | None = Query(None, description="Start (Unix ms)"),
    to_ts: int | None = Query(None, description="End (Unix ms)"),
    worker_name: str | None = Query(None, description="Filter by worker name"),
    db: AsyncSession = Depends(get_db),
):
    """Daily active % per worker within a date range."""
    from_dt, to_dt = _default_range(from_ts, to_ts)

    stmt = (
        select(
            Worker.name,
            func.date(Session.started_at).label("day"),
            func.avg(SessionAggregate.active_pct).label("active_pct"),
        )
        .join(Session, Session.worker_id == Worker.id)
        .join(SessionAggregate, SessionAggregate.session_id == Session.id)
        .where(Session.started_at >= from_dt)
        .where(Session.started_at <= to_dt)
    )
    if worker_name:
        stmt = stmt.where(Worker.name == worker_name)
    stmt = stmt.group_by(Worker.name, func.date(Session.started_at)).order_by("day")

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "worker": row.name,
            "day": str(row.day),
            "active_pct": round(float(row.active_pct or 0), 1),
        }
        for row in rows
    ]


@router.get("/heatmap")
async def get_heatmap(
    from_ts: int | None = Query(None),
    to_ts: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Worker × hour-of-day activity grid. Returns count of events per worker per hour."""
    from_dt, to_dt = _default_range(from_ts, to_ts)

    stmt = (
        select(
            Worker.name,
            extract("hour", ActivityEvent.ts).label("hour"),
            func.count().label("count"),
        )
        .join(Session, Session.id == ActivityEvent.session_id)
        .join(Worker, Worker.id == Session.worker_id)
        .where(ActivityEvent.ts >= from_dt)
        .where(ActivityEvent.ts <= to_dt)
        .group_by(Worker.name, extract("hour", ActivityEvent.ts))
        .order_by(Worker.name, "hour")
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Group by worker
    heatmap: dict[str, dict[int, int]] = {}
    for row in rows:
        w = row.name
        h = int(row.hour)
        if w not in heatmap:
            heatmap[w] = {i: 0 for i in range(24)}
        heatmap[w][h] = int(row.count)

    return [
        {"worker": w, "hours": hours}
        for w, hours in heatmap.items()
    ]


@router.get("/ranking")
async def get_ranking(
    from_ts: int | None = Query(None),
    to_ts: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Workers ranked by average productivity (active_pct)."""
    from_dt, to_dt = _default_range(from_ts, to_ts)

    stmt = (
        select(
            Worker.name,
            func.avg(SessionAggregate.active_pct).label("avg_active"),
            func.avg(SessionAggregate.idle_pct).label("avg_idle"),
            func.sum(SessionAggregate.alert_count).label("total_alerts"),
            func.count(Session.id).label("session_count"),
        )
        .join(Session, Session.worker_id == Worker.id)
        .join(SessionAggregate, SessionAggregate.session_id == Session.id)
        .where(Session.started_at >= from_dt)
        .where(Session.started_at <= to_dt)
        .group_by(Worker.name)
        .order_by(func.avg(SessionAggregate.active_pct).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "worker": row.name,
            "avg_active_pct": round(float(row.avg_active or 0), 1),
            "avg_idle_pct": round(float(row.avg_idle or 0), 1),
            "total_alerts": int(row.total_alerts or 0),
            "session_count": int(row.session_count),
        }
        for row in rows
    ]


@router.get("/state-breakdown")
async def get_state_breakdown(
    from_ts: int | None = Query(None),
    to_ts: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Per-worker state distribution (count of events by label)."""
    from_dt, to_dt = _default_range(from_ts, to_ts)

    stmt = (
        select(
            Worker.name,
            ActivityEvent.label,
            func.count().label("count"),
        )
        .join(Session, Session.id == ActivityEvent.session_id)
        .join(Worker, Worker.id == Session.worker_id)
        .where(ActivityEvent.ts >= from_dt)
        .where(ActivityEvent.ts <= to_dt)
        .group_by(Worker.name, ActivityEvent.label)
        .order_by(Worker.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Group by worker
    breakdown: dict[str, dict[str, int]] = {}
    for row in rows:
        w = row.name
        label = row.label.value if hasattr(row.label, "value") else str(row.label)
        if w not in breakdown:
            breakdown[w] = {"sewing": 0, "idle": 0, "adjusting": 0, "break": 0, "error": 0}
        breakdown[w][label] = int(row.count)

    return [
        {"worker": w, **states}
        for w, states in breakdown.items()
    ]


@router.get("/insights")
async def get_insights(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("supervisor", "factory_admin", "super_admin"))
):
    """
    Fetch AI-generated root-cause insights for the given timeframe.
    Requires at least supervisor role.
    """
    insights = await generate_insights(db, days)
    return insights
