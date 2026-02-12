"""
Industrial Wearable AI — Seed 7 demo workers with 45 days of session/event history.
Run from backend/: python seed_demo_workers.py
W01 is your real device; W02–W08 are sample workers for demo/judges.
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ActivityEvent, ActivityLabel, Session, SessionAggregate, Worker
from app.services.event_service import update_session_aggregate

# W01 = real device; W02–W08 = sample workers for demo
ALL_WORKER_IDS = ["W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08"]
SAMPLE_WORKER_IDS = ["W02", "W03", "W04", "W05", "W06", "W07", "W08"]
DAYS_HISTORY = 45
EVENTS_PER_SESSION = 60
LABELS = [
    (ActivityLabel.SEWING, 0.5),
    (ActivityLabel.IDLE, 0.25),
    (ActivityLabel.ADJUSTING, 0.15),
    (ActivityLabel.BREAK, 0.05),
    (ActivityLabel.ERROR, 0.05),
]


def _random_label():
    r = random.random()
    for label, p in LABELS:
        r -= p
        if r <= 0:
            return label
    return ActivityLabel.SEWING


async def seed_demo():
    async with AsyncSessionLocal() as db:
        for name in ALL_WORKER_IDS:
            result = await db.execute(select(Worker).where(Worker.name == name))
            if result.scalar_one_or_none():
                print(f"Worker {name} already exists, skipping.")
                continue
            w = Worker(name=name, role="Operator")
            db.add(w)
            await db.flush()
            print(f"Created worker {name}")

        await db.commit()

    async with AsyncSessionLocal() as db:
        for name in SAMPLE_WORKER_IDS:
            result = await db.execute(select(Worker).where(Worker.name == name))
            worker = result.scalar_one_or_none()
            if not worker:
                continue

            now = datetime.now(timezone.utc)
            for day_offset in range(DAYS_HISTORY):
                day_start = (now - timedelta(days=day_offset)).replace(
                    hour=6, minute=0, second=0, microsecond=0
                )
                session_start = day_start
                session_end = day_start + timedelta(hours=8)
                result = await db.execute(
                    select(Session).where(
                        Session.worker_id == worker.id,
                        Session.started_at >= session_start,
                        Session.started_at < session_start + timedelta(days=1),
                    )
                )
                if result.scalars().first():
                    continue
                session = Session(
                    worker_id=worker.id,
                    started_at=session_start,
                    ended_at=session_end,
                )
                db.add(session)
                await db.flush()

                interval_sec = 8 * 3600 / EVENTS_PER_SESSION
                for i in range(EVENTS_PER_SESSION):
                    ts = session_start + timedelta(seconds=i * interval_sec)
                    label = _random_label()
                    risk_fatigue = label == ActivityLabel.IDLE and random.random() < 0.2
                    risk_ergo = random.random() < 0.05
                    ev = ActivityEvent(
                        session_id=session.id,
                        ts=ts,
                        label=label,
                        risk_ergo=risk_ergo,
                        risk_fatigue=risk_fatigue,
                    )
                    db.add(ev)

                await update_session_aggregate(db, session.id)

            print(f"Seeded {DAYS_HISTORY} days of sessions for {name}")

        await db.commit()
        print("Done. W01 + W02–W08 workers created; W02–W08 have 45 days of sample history.")


if __name__ == "__main__":
    asyncio.run(seed_demo())
