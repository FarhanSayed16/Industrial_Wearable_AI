"""
Industrial Wearable AI — Workers API
GET /api/workers — return list of workers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.database import get_db
from app.models import Worker
from app.schemas import WorkerOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["workers"])


@router.get("/workers", response_model=list[WorkerOut])
async def get_workers(db: AsyncSession = Depends(get_db)):
    """Return all workers."""
    stmt = select(Worker).order_by(Worker.name)
    result = await db.execute(stmt)
    workers = result.scalars().all()
    return workers
