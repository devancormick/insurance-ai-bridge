"""Helper utilities."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4()).replace("-", "")[:16]
    if prefix:
        return f"{prefix}-{unique_id.upper()}"
    return unique_id.upper()


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def calculate_age(date_of_birth: datetime) -> int:
    """
    Calculate age from date of birth.
    
    Args:
        date_of_birth: Date of birth
        
    Returns:
        Age in years
    """
    today = datetime.utcnow().date()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """
    Mask sensitive data (e.g., SSN last 4 digits).
    
    Args:
        data: Data to mask
        mask_char: Character to use for masking
        
    Returns:
        Masked data
    """
    if len(data) <= 4:
        return mask_char * len(data)
    return mask_char * (len(data) - 4) + data[-4:]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    return sanitized


def paginate_results(
    items: list, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list of results.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Dictionary with paginated results and metadata
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

