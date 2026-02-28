from typing import Dict, Any, List
import httpx
import logging
from app.models.activity_event import ActivityEvent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WebhookSubscription(BaseModel):
    url: str
    events: List[str] # e.g. ["anomaly", "fatigue_alert", "session_end"]

# In-memory mock for registered webhooks (would be DB in prod)
REGISTERED_WEBHOOKS: List[WebhookSubscription] = []

async def dispatch_webhook(event_type: str, payload: Dict[str, Any]):
    """Dispatches a generic JSON POST to securely registered webhook URLs listening to this event type."""
    async with httpx.AsyncClient() as client:
        for sub in REGISTERED_WEBHOOKS:
            if event_type in sub.events or "*" in sub.events:
                try:
                    # Execute async POST request
                    response = await client.post(sub.url, json={
                        "event": event_type,
                        "data": payload
                    }, timeout=5.0)
                    if response.status_code >= 400:
                        logger.warning(f"Webhook {sub.url} failed with status {response.status_code}")
                except Exception as e:
                    logger.error(f"Error dispatching webhook to {sub.url}: {e}")

async def register_webhook_subscription(url: str, events: List[str]):
    REGISTERED_WEBHOOKS.append(WebhookSubscription(url=url, events=events))
    logger.info(f"Registered new webhook for {url}")
