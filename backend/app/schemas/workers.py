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
