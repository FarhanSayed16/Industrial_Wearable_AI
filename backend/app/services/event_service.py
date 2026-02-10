"""
Industrial Wearable AI — Event Aggregation Service
Computes session aggregates from activity_events.
"""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityEvent, ActivityLabel, SessionAggregate


async def update_session_aggregate(db: AsyncSession, session_id) -> SessionAggregate:
    """
    Query activity_events for session; compute percentages; upsert session_aggregates.
    - active_pct = (sewing + adjusting) / total
    - idle_pct, adjusting_pct, error_pct = count/total
    - alert_count = events where risk_ergo or risk_fatigue = true
    """
    # Count by label
    stmt = (
        select(ActivityEvent.label, func.count(ActivityEvent.id).label("cnt"))
        .where(ActivityEvent.session_id == session_id)
        .group_by(ActivityEvent.label)
    )
    result = await db.execute(stmt)
    counts = {row.label: row.cnt for row in result.fetchall()}

    total = sum(counts.values())
    if total == 0:
        sewing = adjusting = idle = err = 0
    else:
        sewing = counts.get(ActivityLabel.SEWING, 0)
        adjusting = counts.get(ActivityLabel.ADJUSTING, 0)
        idle = counts.get(ActivityLabel.IDLE, 0)
        err = counts.get(ActivityLabel.ERROR, 0)
        # break not included in active

    active_pct = (sewing + adjusting) / total * 100 if total else None
    idle_pct = idle / total * 100 if total else None
    adjusting_pct = adjusting / total * 100 if total else None
    error_pct = err / total * 100 if total else None

    # Alert count: events with risk_ergo or risk_fatigue
    alert_stmt = (
        select(func.count(ActivityEvent.id))
        .where(ActivityEvent.session_id == session_id)
        .where(or_(ActivityEvent.risk_ergo == True, ActivityEvent.risk_fatigue == True))
    )
    alert_result = await db.execute(alert_stmt)
    alert_count = alert_result.scalar() or 0

    # Upsert session_aggregates
    existing = await db.get(SessionAggregate, session_id)
    if existing:
        existing.active_pct = active_pct
        existing.idle_pct = idle_pct
        existing.adjusting_pct = adjusting_pct
        existing.error_pct = error_pct
        existing.alert_count = alert_count
        await db.flush()
        return existing
    else:
        agg = SessionAggregate(
            session_id=session_id,
            active_pct=active_pct,
            idle_pct=idle_pct,
            adjusting_pct=adjusting_pct,
            error_pct=error_pct,
            alert_count=alert_count,
        )
        db.add(agg)
        await db.flush()
        return agg
