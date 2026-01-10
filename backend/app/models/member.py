"""Member database model."""
from sqlalchemy import Column, String, DateTime, Date
from datetime import datetime
from app.models.base import Base


class Member(Base):
    """Member model."""
    __tablename__ = "members"
    
    id = Column(String, primary_key=True)
    member_id = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

