"""
Industrial Wearable AI — Activity Event Model
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.session import Session


class ActivityLabel(str, enum.Enum):
    """Activity labels from ML classifier."""

    SEWING = "sewing"
    IDLE = "idle"
    ADJUSTING = "adjusting"
    ERROR = "error"
    BREAK = "break"


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    label: Mapped[ActivityLabel] = mapped_column(
        Enum(ActivityLabel),
        nullable=False,
    )
    risk_ergo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    risk_fatigue: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_activity_events_session_id_ts", "session_id", "ts"),
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="activity_events",
    )
