"""
Industrial Wearable AI — Event Schemas
"""
from typing import Optional

from pydantic import BaseModel, Field


class ActivityEventIn(BaseModel):
    """Single activity event from edge (ts in Unix ms)."""

    ts: int = Field(..., description="Unix timestamp in milliseconds")
    label: str = Field(..., description="sewing|idle|adjusting|error|break")
    risk_ergo: bool = False
    risk_fatigue: bool = False


class EventBatch(BaseModel):
    """Batch of activity events from edge."""

    device_id: Optional[str] = None
    worker_id: str = Field(..., description="Worker identifier (e.g. W01)")
    events: list[ActivityEventIn] = Field(..., min_length=1)
