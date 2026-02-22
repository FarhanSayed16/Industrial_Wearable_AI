from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.session import Session
from app.models.activity_event import ActivityEvent
from app.models.session_aggregate import SessionAggregate
from app.models.worker import Worker
from app.dependencies import require_role
from app.services.report_generator import generate_shift_report_pdf

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/session/{session_id}/pdf")
async def download_session_pdf(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("supervisor", "factory_admin", "super_admin"))
):
    """
    Generate and download a comprehensive PDF report for a specific session.
    Requires at least supervisor role.
    """
    # 1. Fetch Session and Worker
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    w_res = await db.execute(select(Worker).where(Worker.id == session.worker_id))
    worker = w_res.scalars().first()
    worker_name = worker.name if worker else "Unknown Worker"

    # 2. Fetch Aggregates
    agg_res = await db.execute(select(SessionAggregate).where(SessionAggregate.session_id == session_id))
    agg = agg_res.scalars().first()
    
    aggregates_dict = {
        'active_pct': agg.active_pct if agg else 0,
        'idle_pct': agg.idle_pct if agg else 0,
        'adjusting_pct': agg.adjusting_pct if agg else 0,
        'error_pct': agg.error_pct if agg else 0,
        'productivity_score': agg.productivity_score if agg else 0,
        'alert_count': agg.alert_count if agg else 0,
    }

    # 3. Fetch Events (ordered by timestamp)
    event_res = await db.execute(select(ActivityEvent).where(ActivityEvent.session_id == session_id).order_by(ActivityEvent.ts.asc()))
    events = event_res.scalars().all()
    events_list = [
        {
            "ts": e.ts,
            "label": e.label,
            "risk_ergo": e.risk_ergo,
            "risk_fatigue": e.risk_fatigue
        }
        for e in events
    ]

    # Generate PDF
    try:
        pdf_bytes = generate_shift_report_pdf(
            session_id=str(session.id),
            worker_name=worker_name,
            started_at=session.started_at,
            ended_at=session.ended_at,
            aggregates=aggregates_dict,
            events=events_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    filename = f"Shift_Report_{worker_name}_{session.started_at.strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
