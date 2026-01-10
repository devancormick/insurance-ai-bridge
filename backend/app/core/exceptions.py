"""Custom exceptions for the application."""
from fastapi import HTTPException, status
from typing import Any, Optional


class InsuranceAIBridgeException(HTTPException):
    """Base exception for Insurance AI Bridge."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ClaimNotFoundError(InsuranceAIBridgeException):
    """Raised when a claim is not found."""
    
    def __init__(self, claim_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )


class MemberNotFoundError(InsuranceAIBridgeException):
    """Raised when a member is not found."""
    
    def __init__(self, member_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member {member_id} not found"
        )


class PolicyNotFoundError(InsuranceAIBridgeException):
    """Raised when a policy is not found."""
    
    def __init__(self, policy_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy {policy_id} not found"
        )


class LLMProcessingError(InsuranceAIBridgeException):
    """Raised when LLM processing fails."""
    
    def __init__(self, detail: str = "LLM processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class PIIHandlingError(InsuranceAIBridgeException):
    """Raised when PII handling fails."""
    
    def __init__(self, detail: str = "PII handling error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DatabaseConnectionError(InsuranceAIBridgeException):
    """Raised when database connection fails."""
    
    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class LegacySystemError(InsuranceAIBridgeException):
    """Raised when legacy system integration fails."""
    
    def __init__(self, system: str, detail: str = "Legacy system error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{system}: {detail}"
        )


class AuthenticationError(InsuranceAIBridgeException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(InsuranceAIBridgeException):
    """Raised when authorization fails."""
    
    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationError(InsuranceAIBridgeException):
    """Raised when validation fails."""
    
    def __init__(self, detail: str = "Validation error", errors: Optional[list] = None):
        error_detail = {"message": detail}
        if errors:
            error_detail["errors"] = errors
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail
        )

