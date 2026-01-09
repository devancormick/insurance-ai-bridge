"""Claim database model."""
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Claim(Base):
    """Claim model."""
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, unique=True, index=True)
    member_id = Column(String, index=True)
    policy_id = Column(String, index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

