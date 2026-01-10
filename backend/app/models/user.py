"""User database model."""
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from app.models.base import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(String(length=255), primary_key=True)
    username = Column(String(length=100), unique=True, index=True, nullable=False)
    email = Column(String(length=255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=255), nullable=False)
    full_name = Column(String(length=255), nullable=True)
    disabled = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

