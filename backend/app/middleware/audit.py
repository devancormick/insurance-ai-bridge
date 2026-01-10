"""Audit logging middleware."""
from fastapi import Request
from typing import Callable
from app.utils.logging import logger
from datetime import datetime
import json


async def audit_log_middleware(request: Request, call_next: Callable):
    """
    Audit log middleware for HIPAA compliance.
    
    Logs all data access without PII for compliance tracking.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response with audit logging
    """
    start_time = datetime.utcnow()
    
    # Extract user info (if authenticated)
    user_id = None
    if hasattr(request.state, "user"):
        user_id = request.state.user.get("username")
    
    # Extract request details (without PII)
    audit_data = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "path": request.url.path,
        "user_id": user_id or "anonymous",
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
    
    # Log request (without PII)
    logger.info(f"AUDIT: {json.dumps(audit_data)}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    
    audit_data.update({
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "completed_at": end_time.isoformat()
    })
    
    logger.info(f"AUDIT_COMPLETE: {json.dumps(audit_data)}")
    
    return response

