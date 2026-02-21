import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "wearable_ai_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.reports"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Schedule background jobs
celery_app.conf.beat_schedule = {
    # Every day at 23:00 UTC (end of day shift)
    "daily-shift-summary-email": {
        "task": "app.tasks.reports.send_daily_summary",
        "schedule": crontab(hour=23, minute=0),
    },
    # Every Monday at 08:00 UTC
    "weekly-digest-email": {
        "task": "app.tasks.reports.send_weekly_digest",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),
    }
}
