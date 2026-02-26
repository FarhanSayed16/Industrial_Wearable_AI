import httpx
import logging
import os

logger = logging.getLogger(__name__)

# Usually read from DB or ENV
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

async def send_slack_alert(worker_name: str, risk_type: str, score: float, timestamp: str):
    """Sends a heavily formatted Block-Kit message to a specific Slack channel when a risk triggers."""
    if not SLACK_WEBHOOK_URL:
        # Silently return if no webhook configured
        return

    # Slack Block Kit styling
    color = "#FFA500" if risk_type == "Ergonomic" else "#FF0000"
    emoji = "⚠️" if risk_type == "Ergonomic" else "🚨"
    
    payload = {
        "text": f"{emoji} {risk_type} Risk Alert: {worker_name}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {risk_type} Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Worker:*\n{worker_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Criticality Score:*\n{score:.2f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time Detected:*\n{timestamp}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Dashboard"
                        },
                        "url": "http://wearable-ai.local/live"
                    }
                ]
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(SLACK_WEBHOOK_URL, json=payload, timeout=5.0)
            res.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to push alert to Slack: {e}")
