"""Tests for validation utilities."""
import pytest
from app.utils.validators import (
    validate_password_strength,
    validate_claim_id,
    validate_member_id,
    validate_policy_id
)


def test_validate_password_strength_valid():
    """Test password validation with valid password."""
    valid_password = "Test@1234"
    is_valid, error = validate_password_strength(valid_password)
    
    assert is_valid is True
    assert error is None


def test_validate_password_strength_too_short():
    """Test password validation with too short password."""
    short_password = "Test@12"
    is_valid, error = validate_password_strength(short_password)
    
    assert is_valid is False
    assert "at least 8 characters" in error.lower()


def test_validate_password_strength_no_uppercase():
    """Test password validation without uppercase."""
    no_upper = "test@1234"
    is_valid, error = validate_password_strength(no_upper)
    
    assert is_valid is False
    assert "uppercase" in error.lower()


def test_validate_password_strength_too_long():
    """Test password validation with too long password."""
    long_password = "A" * 73  # bcrypt limit is 72 bytes
    is_valid, error = validate_password_strength(long_password)
    
    assert is_valid is False
    assert "72" in error


def test_validate_claim_id():
    """Test claim ID validation."""
    assert validate_claim_id("CLM-12345") is True
    assert validate_claim_id("CLM-99999") is True
    assert validate_claim_id("INVALID") is False
    assert validate_claim_id("CLM-123") is False  # Too short
    assert validate_claim_id("12345") is False


def test_validate_member_id():
    """Test member ID validation."""
    assert validate_member_id("MEM-12345") is True
    assert validate_member_id("MEM-99999") is True
    assert validate_member_id("INVALID") is False


def test_validate_policy_id():
    """Test policy ID validation."""
    assert validate_policy_id("POL-12345") is True
    assert validate_policy_id("POL-99999") is True
    assert validate_policy_id("INVALID") is False

