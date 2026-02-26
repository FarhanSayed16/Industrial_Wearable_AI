"""
Industrial Wearable AI — Worker Model
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.session import Session
    from app.models.consent import ConsentRecord


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=True)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships (one-to-one with Device; no back_populates to avoid circular ref)
    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        foreign_keys=[device_id],
        uselist=False,
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="worker",
        foreign_keys="Session.worker_id",
    )
    consent_record: Mapped[Optional["ConsentRecord"]] = relationship(
        "ConsentRecord",
        back_populates="worker",
        uselist=False,
    )
