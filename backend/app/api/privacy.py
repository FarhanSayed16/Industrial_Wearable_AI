"""
Industrial Wearable AI — Privacy & Consent API
GET /api/privacy/consent/{worker_id} - View a worker's consent status
POST /api/privacy/consent/{worker_id} - Update a worker's consent status
DELETE /api/privacy/data/{worker_id} - Admin action to purge all worker data (Right to Deletion)
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models import ActivityEvent, ConsentRecord, Session, SessionAggregate, Worker

router = APIRouter(prefix="/api/privacy", tags=["privacy"])

class ConsentUpdate(BaseModel):
    retention_days: str = "365"
    opt_in_data_collection: bool = True
    opt_in_ai_analysis: bool = True

@router.get("/consent/{worker_id}")
async def get_consent(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("supervisor", "factory_admin", "super_admin"))
):
    """Retrieve the privacy consent record for a specific worker."""
    stmt = select(ConsentRecord).where(ConsentRecord.worker_id == worker_id)
    result = await db.execute(stmt)
    consent = result.scalar_one_or_none()
    
    if not consent:
        return {"status": "no_record", "opt_in_data_collection": False}
        
    return {
        "status": "consented",
        "consented_at": consent.consented_at.isoformat(),
        "retention_days": consent.retention_days,
        "opt_in_data_collection": consent.opt_in_data_collection,
        "opt_in_ai_analysis": consent.opt_in_ai_analysis
    }

@router.post("/consent/{worker_id}")
async def update_consent(
    worker_id: UUID,
    payload: ConsentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("supervisor", "factory_admin", "super_admin"))
):
    """Update or create a privacy consent record for a specific worker."""
    stmt = select(ConsentRecord).where(ConsentRecord.worker_id == worker_id)
    result = await db.execute(stmt)
    consent = result.scalar_one_or_none()

    if not consent:
        consent = ConsentRecord(worker_id=worker_id)
        db.add(consent)

    consent.consented_at = datetime.now(timezone.utc)
    consent.ip_address = request.client.host if request.client else None
    consent.retention_days = payload.retention_days
    consent.opt_in_data_collection = payload.opt_in_data_collection
    consent.opt_in_ai_analysis = payload.opt_in_ai_analysis
    
    await db.commit()
    return {"status": "updated"}

@router.delete("/data/{worker_id}")
async def purge_worker_data(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("factory_admin", "super_admin"))
):
    """
    Right to Deletion: Hard-purge all of a worker's sensor and aggregate data.
    Requires Admin privileges.
    """
    # 1. Get all sessions for this worker
    stmt = select(Session.id).where(Session.worker_id == worker_id)
    result = await db.execute(stmt)
    session_ids = [row[0] for row in result.all()]
    
    deleted_events = 0
    deleted_aggregates = 0
    deleted_sessions = 0
    
    if session_ids:
        # 2. Delete all events linked to these sessions
        del_events = await db.execute(delete(ActivityEvent).where(ActivityEvent.session_id.in_(session_ids)))
        deleted_events = del_events.rowcount
        
        # 3. Delete all aggregates
        del_aggs = await db.execute(delete(SessionAggregate).where(SessionAggregate.session_id.in_(session_ids)))
        deleted_aggregates = del_aggs.rowcount
        
        # 4. Delete the sessions themselves
        del_sessions = await db.execute(delete(Session).where(Session.worker_id == worker_id))
        deleted_sessions = del_sessions.rowcount

    await db.commit()
    return {
        "status": "purged",
        "worker_id": str(worker_id),
        "deleted_events": deleted_events,
        "deleted_sessions": deleted_sessions
    }
