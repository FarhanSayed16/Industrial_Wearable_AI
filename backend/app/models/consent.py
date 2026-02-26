"""
Industrial Wearable AI — Consent Model
Tracks worker privacy opt-ins and data retention policies.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class ConsentRecord(Base):
    """
    ConsentRecord representing a worker's privacy preferences and consent status.
    Uses a 1:1 relationship with Worker through the worker_id ForeignKey.
    """
    __tablename__ = "consent_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # When did the worker provide consent?
    consented_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Audit trail details
    ip_address = Column(String(64), nullable=True) # E.g., from the tablet used to sign in
    
    # Privacy preferences
    retention_days = Column(String(20), default="365", nullable=False) # e.g. "30", "90", "365", "indefinite"
    opt_in_data_collection = Column(Boolean, default=True, nullable=False)
    opt_in_ai_analysis = Column(Boolean, default=True, nullable=False)
    
    # Relationship to Worker
    worker = relationship("Worker", back_populates="consent_record")
