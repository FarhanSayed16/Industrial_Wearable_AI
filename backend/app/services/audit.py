"""
Industrial Wearable AI — Audit Service
Records significant actions for traceability.
"""
from datetime import datetime, timezone
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    action: str,
    resource: str | None = None,
    details: str | None = None,
    user: User | None = None,
    ip_address: str | None = None,
):
    """Log an audit event."""
    try:
        entry = AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
        )
        db.add(entry)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log '{action}': {e}")
        # Typically we don't want an audit log failure to break the main request
        # but in strict compliance environments, you might raise here.
