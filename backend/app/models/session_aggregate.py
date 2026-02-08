"""
Industrial Wearable AI — Session Aggregate Model
Per-session summary statistics.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.session import Session


class SessionAggregate(Base):
    __tablename__ = "session_aggregates"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    active_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    idle_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    adjusting_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alert_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="aggregate",
    )
