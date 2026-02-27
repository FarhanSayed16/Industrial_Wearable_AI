"""
Industrial Wearable AI — Celery Tasks for automated reports.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from celery_config import celery_app
from app.services.email import send_email_sync

# Since Celery is sync and SQLAlchemy is async in this project,
# we need to bridge the gap by running an event loop if we need DB access.
# For demonstration purposes, we'll implement a mock summary.
# In a real app, we'd use async_to_sync or raw psycopg2 queries for Celery.

log = logging.getLogger(__name__)

@celery_app.task
def send_daily_summary():
    """Compiles and sends a daily shift summary via email."""
    log.info("Starting daily_summary task...")
    
    # Mock data fetch
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    body = f"""
    Hello Supervisor,
    
    Here is the automated daily shift summary for {today}.
    
    - Total Active Workers: 12
    - Average Productivity: 82%
    - Total Ergonomic Alerts: 5
    - Total Fatigue Alerts: 2
    
    Please review the dashboard for detailed analytics.
    
    Regards,
    Industrial Wearable AI System
    """
    
    send_email_sync(
        to_address="supervisor@factory.com",
        subject=f"Daily Shift Summary - {today}",
        body=body
    )
    return f"Daily summary sent for {today}"

@celery_app.task
def send_weekly_digest():
    """Compiles and sends a weekly digest via email."""
    log.info("Starting weekly_digest task...")
    
    week_start = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    
    body = """
    Hello Admin,
    
    Here is the automated weekly digest.
    
    - Best Performing Station: Station 3 (91% Productivity)
    - Highest Risk Station: Station 1 (14 Alerts)
    - Recommended Action: Review ergonomic setup at Station 1.
    
    Regards,
    Industrial Wearable AI System
    """
    
    send_email_sync(
        to_address="admin@factory.com",
        subject=f"Weekly Operations Digest - Week of {week_start}",
        body=body
    )
    return "Weekly digest sent"
