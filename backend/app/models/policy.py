"""Policy database model."""
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.models.base import Base


class Policy(Base):
    """Policy model."""
    __tablename__ = "policies"
    
    id = Column(String, primary_key=True)
    policy_id = Column(String, unique=True, index=True)
    policy_number = Column(String, index=True, nullable=True)
    member_id = Column(String, index=True, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    document_text = Column(Text, nullable=True)

