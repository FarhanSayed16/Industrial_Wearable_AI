"""
Industrial Wearable AI — Session Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionOut(BaseModel):
    """Session response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    worker_id: UUID
    worker_name: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    shift_label: Optional[str] = None


class SessionSummaryOut(BaseModel):
    """Session aggregate summary response."""

    session_id: UUID
    worker_id: str
    active_pct: Optional[float] = None
    idle_pct: Optional[float] = None
    adjusting_pct: Optional[float] = None
    error_pct: Optional[float] = None
    alert_count: int = 0
