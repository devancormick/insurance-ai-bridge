"""Policy database model."""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Policy(Base):
    """Policy model."""
    __tablename__ = "policies"
    
    id = Column(String, primary_key=True)
    policy_id = Column(String, unique=True, index=True)
    policy_number = Column(String, index=True)
    member_id = Column(String, index=True)
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    document_text = Column(Text, nullable=True)

