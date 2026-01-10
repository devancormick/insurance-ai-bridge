"""Claim database model."""
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.models.base import Base


class Claim(Base):
    """Claim model."""
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, unique=True, index=True)
    member_id = Column(String, index=True)
    policy_id = Column(String, index=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

