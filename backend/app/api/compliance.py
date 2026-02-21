from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.services.compliance import generate_compliance_metrics

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

@router.get("/metrics")
async def get_compliance_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("supervisor", "factory_admin", "super_admin"))
):
    """
    Fetch ISO 45001 aligned occupational health and safety metrics.
    """
    metrics = await generate_compliance_metrics(db, days)
    return metrics
