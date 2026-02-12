"""
Industrial Wearable AI — Worker Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkerOut(BaseModel):
    """Worker response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    role: Optional[str] = None
    device_id: Optional[UUID] = None
    created_at: datetime


class WorkerHistoryEntry(BaseModel):
    """Single session summary for a worker's history."""

    session_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    active_pct: Optional[float] = None
    idle_pct: Optional[float] = None
    adjusting_pct: Optional[float] = None
    error_pct: Optional[float] = None
    alert_count: int = 0
