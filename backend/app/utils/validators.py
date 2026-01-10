"""Validation utilities."""
import re
from typing import Optional


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 72:
        return False, "Password cannot be longer than 72 characters (bcrypt limit)"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_claim_id(claim_id: str) -> bool:
    """Validate claim ID format."""
    pattern = r'^CLM-\d{5,}$'
    return bool(re.match(pattern, claim_id))


def validate_member_id(member_id: str) -> bool:
    """Validate member ID format."""
    pattern = r'^MEM-\d{5,}$'
    return bool(re.match(pattern, member_id))


def validate_policy_id(policy_id: str) -> bool:
    """Validate policy ID format."""
    pattern = r'^POL-\d{5,}$'
    return bool(re.match(pattern, policy_id))

