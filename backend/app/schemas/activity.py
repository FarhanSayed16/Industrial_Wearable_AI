"""
Industrial Wearable AI — Activity timeline schema for chart API.
"""
from pydantic import BaseModel


class TimelineBucketOut(BaseModel):
    """One time bucket with counts per activity label (minute = "HH:MM")."""

    minute: str
    sewing: int = 0
    adjusting: int = 0
    idle: int = 0
    break_: int = 0  # serialized as "break" in response
    error: int = 0

    model_config = {"populate_by_name": True}
