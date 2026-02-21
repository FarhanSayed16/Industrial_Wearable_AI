"""
Industrial Wearable AI — Data Export API
Export sessions and analytics data as CSV.
"""
import io
import csv
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models import Session, SessionAggregate, Worker, User
from app.services.audit import log_action

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/sessions")
async def export_sessions_csv(
    user: User = Depends(require_role("super_admin", "factory_admin", "supervisor")),
    db: AsyncSession = Depends(get_db),
):
    """Export all session metadata + aggregates as CSV."""
    stmt = (
        select(Session)
        .options(selectinload(Session.worker))
        .order_by(Session.started_at.desc())
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    # Also fetch aggregates manually or just join them
    stmt_agg = select(SessionAggregate)
    res_agg = await db.execute(stmt_agg)
    agg_map = {agg.session_id: agg for agg in res_agg.scalars().all()}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Session ID", "Worker Name", "Worker Role", "Start Time", "End Time",
        "Active %", "Idle %", "Adjusting %", "Error %", "Alert Count", "Notes"
    ])

    for s in sessions:
        agg = agg_map.get(s.id)
        writer.writerow([
            str(s.id),
            s.worker.name if s.worker else "Unknown",
            s.worker.role if s.worker else "",
            s.started_at.isoformat() if s.started_at else "",
            s.ended_at.isoformat() if s.ended_at else "",
            round(agg.active_pct, 1) if agg and agg.active_pct is not None else "",
            round(agg.idle_pct, 1) if agg and agg.idle_pct is not None else "",
            round(agg.adjusting_pct, 1) if agg and agg.adjusting_pct is not None else "",
            round(agg.error_pct, 1) if agg and agg.error_pct is not None else "",
            agg.alert_count if agg else 0,
            s.notes or "",
        ])

    await log_action(db, "export_data", "sessions_csv", f"Exported {len(sessions)} sessions", user)

    output.seek(0)
    filename = f"sessions_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
