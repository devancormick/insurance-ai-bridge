"""Tests for custom exceptions."""
import pytest
from fastapi import status
from app.core.exceptions import (
    InsuranceAIBridgeException,
    ClaimNotFoundError,
    MemberNotFoundError,
    PolicyNotFoundError,
    LLMProcessingError,
    PIIHandlingError,
    AuthenticationError,
    AuthorizationError,
    ValidationError
)


def test_claim_not_found_error():
    """Test ClaimNotFoundError exception."""
    claim_id = "CLM-99999"
    error = ClaimNotFoundError(claim_id)
    
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert claim_id in error.detail
    assert "not found" in error.detail.lower()


def test_member_not_found_error():
    """Test MemberNotFoundError exception."""
    member_id = "MEM-99999"
    error = MemberNotFoundError(member_id)
    
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert member_id in error.detail


def test_policy_not_found_error():
    """Test PolicyNotFoundError exception."""
    policy_id = "POL-99999"
    error = PolicyNotFoundError(policy_id)
    
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert policy_id in error.detail


def test_authentication_error():
    """Test AuthenticationError exception."""
    error = AuthenticationError("Invalid credentials")
    
    assert error.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in error.headers
    assert error.headers["WWW-Authenticate"] == "Bearer"


def test_authorization_error():
    """Test AuthorizationError exception."""
    error = AuthorizationError("Access denied")
    
    assert error.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in error.detail


def test_validation_error():
    """Test ValidationError exception."""
    errors = [{"field": "claim_id", "message": "Required"}]
    error = ValidationError("Validation failed", errors=errors)
    
    assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert error.detail["errors"] == errors

