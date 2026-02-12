"""
Industrial Wearable AI — Activity timeline API
GET /api/activity/timeline?from_ts=&to_ts= (Unix ms) — bucketed activity for charts.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.database import get_db
from app.models import ActivityEvent
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["activity"])


@router.get("/activity/timeline")
async def get_activity_timeline(
    from_ts: int = Query(..., description="Start time (Unix ms)"),
    to_ts: int = Query(..., description="End time (Unix ms)"),
    bucket_minutes: int = Query(1, ge=1, le=60, description="Bucket size in minutes"),
    db: AsyncSession = Depends(get_db),
):
    """Return activity events bucketed by time for the given range. For past timeline chart."""
    from_dt = datetime.fromtimestamp(from_ts / 1000.0, tz=timezone.utc)
    to_dt = datetime.fromtimestamp(to_ts / 1000.0, tz=timezone.utc)
    if to_dt <= from_dt:
        return []

    stmt = (
        select(ActivityEvent.ts, ActivityEvent.label)
        .where(ActivityEvent.ts >= from_dt)
        .where(ActivityEvent.ts <= to_dt)
        .order_by(ActivityEvent.ts)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Bucket by minute (or bucket_minutes)
    bucket_sec = bucket_minutes * 60
    buckets: dict[int, dict[str, int]] = {}
    labels = ("sewing", "adjusting", "idle", "break", "error")

    for ts, label in rows:
        key = int(ts.timestamp() // bucket_sec) * bucket_sec
        if key not in buckets:
            buckets[key] = {s: 0 for s in labels}
        label_str = label.value if hasattr(label, "value") else str(label).lower()
        if label_str in buckets[key]:
            buckets[key][label_str] += 1

    # Fill gaps and format
    out = []
    t = int(from_dt.timestamp() // bucket_sec) * bucket_sec
    end = int(to_dt.timestamp() // bucket_sec) * bucket_sec
    while t <= end:
        counts = buckets.get(t, {s: 0 for s in labels})
        dt = datetime.fromtimestamp(t, tz=timezone.utc)
        minute_str = dt.strftime("%H:%M")
        out.append({
            "minute": minute_str,
            "sewing": counts.get("sewing", 0),
            "adjusting": counts.get("adjusting", 0),
            "idle": counts.get("idle", 0),
            "break": counts.get("break", 0),
            "error": counts.get("error", 0),
        })
        t += bucket_sec

    return out
