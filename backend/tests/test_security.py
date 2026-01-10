"""Tests for security utilities."""
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token
from jose import jwt
from app.config import settings
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Verify hash is different from original
    assert hashed != password
    
    # Verify password can be verified
    assert verify_password(password, hashed) is True
    
    # Verify wrong password fails
    assert verify_password("wrong_password", hashed) is False


def test_token_creation():
    """Test JWT token creation."""
    data = {"sub": "testuser", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token can be decoded
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    
    assert payload["sub"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_token_expiration():
    """Test token expiration."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires_delta)
    
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    
    # Verify expiration is set
    assert "exp" in payload
    
    # Verify expiration is in the future
    from datetime import datetime
    exp_time = datetime.fromtimestamp(payload["exp"])
    assert exp_time > datetime.utcnow()

