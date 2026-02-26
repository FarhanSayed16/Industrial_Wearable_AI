"""
Industrial Wearable AI — Compliance Service
Calculates metrics aligned with ISO 45001 occupational health and safety standards.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, Float, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.session_aggregate import SessionAggregate
from app.models.activity_event import ActivityEvent
from app.models.worker import Worker

async def generate_compliance_metrics(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Generates an audit report object reflecting ISO 45001 KPIs."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # 1. Total Hours at Risk (Ergo + Fatigue)
    risk_stmt = select(func.count(ActivityEvent.id)).where(
        ActivityEvent.ts >= int(since.timestamp() * 1000),
        (ActivityEvent.risk_ergo == True) | (ActivityEvent.risk_fatigue == True)
    )
    risk_res = await db.execute(risk_stmt)
    total_risk_events = risk_res.scalar() or 0
    # Assume each risk event roughly represents 1 minute of exposure for this metric
    hours_at_risk = round(total_risk_events / 60, 2)

    # 2. Break Compliance
    # ISO 45001 emphasizes adequate rest. We measure % of sessions longer than 4 hours that contain a break.
    sessions_stmt = select(Session).where(Session.started_at >= since)
    sessions_res = await db.execute(sessions_stmt)
    sessions = sessions_res.scalars().all()
    
    long_sessions = [s for s in sessions if s.ended_at and (s.ended_at - s.started_at).total_seconds() > 4 * 3600]
    break_compliant_sessions = 0
    
    for s in long_sessions:
        agg_stmt = select(SessionAggregate.break_pct).where(SessionAggregate.session_id == s.id)
        agg_res = await db.execute(agg_stmt)
        break_pct = agg_res.scalar() or 0
        
        # If total break time > 5% of a 4+ hour shift (~12 minutes), we count it as compliant
        if break_pct > 5.0:
            break_compliant_sessions += 1
            
    break_compliance_pct = 100.0
    if long_sessions:
        break_compliance_pct = round((break_compliant_sessions / len(long_sessions)) * 100, 1)

    # 3. Overall Incident Rate (Alerts per 100 hours worked)
    time_stmt = select(func.sum(SessionAggregate.duration_min)).where(
        Session.started_at >= since
    ).join(Session, Session.id == SessionAggregate.session_id)
    time_res = await db.execute(time_stmt)
    total_minutes_worked = time_res.scalar() or 0
    total_hours_worked = float(total_minutes_worked) / 60.0
    
    incident_rate = 0.0
    if total_hours_worked > 0:
        incident_rate = round((total_risk_events / total_hours_worked) * 100, 2)

    # 4. Top Worker at Risk (Anonymized or directly named for admin)
    top_risk_stmt = (
        select(Worker.name, cast(func.sum(SessionAggregate.alert_count), Float).label("total_alerts"))
        .join(Session, Session.worker_id == Worker.id)
        .join(SessionAggregate, SessionAggregate.session_id == Session.id)
        .where(Session.started_at >= since)
        .group_by(Worker.name)
        .order_by(func.sum(SessionAggregate.alert_count).desc())
        .limit(1)
    )
    top_risk_res = await db.execute(top_risk_stmt)
    top_risk_worker = top_risk_res.first()
    
    highest_risk_worker = top_risk_worker.name if top_risk_worker else "N/A"
    
    return {
        "period_days": days,
        "hours_at_risk": hours_at_risk,
        "break_compliance_pct": break_compliance_pct,
        "incident_rate_per_100h": incident_rate,
        "total_hours_worked": round(total_hours_worked, 1),
        "highest_risk_worker": highest_risk_worker
    }
