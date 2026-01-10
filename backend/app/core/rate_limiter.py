"""Rate limiting middleware."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio
from app.utils.logging import logger


class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks."""
        now = datetime.utcnow()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = now - timedelta(hours=1)
        keys_to_remove = []
        
        for key, timestamps in self.requests.items():
            self.requests[key] = [ts for ts in timestamps if ts > cutoff_time]
            if not self.requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]
        
        self.last_cleanup = now
        logger.debug(f"Rate limiter cleanup: {len(self.requests)} active keys")
    
    def is_allowed(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (usually IP address or user ID)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        self._cleanup_old_entries()
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Filter requests within the time window
        self.requests[key] = [
            ts for ts in self.requests[key] if ts > window_start
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[key])
        
        if request_count >= max_requests:
            remaining = 0
            return False, remaining
        
        # Add current request timestamp
        self.requests[key].append(now)
        remaining = max_requests - request_count - 1
        
        return True, remaining


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(
    request: Request,
    call_next,
    max_requests: int = 100,
    window_seconds: int = 60
):
    """
    Rate limiting middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        
    Returns:
        Response or rate limit error
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Get rate limit key (use IP or user ID if authenticated)
    # TODO: Extract user ID from JWT token if available
    key = f"{client_ip}:{request.url.path}"
    
    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(
        key, max_requests, window_seconds
    )
    
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": window_seconds
            },
            headers={
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(window_seconds),
                "Retry-After": str(window_seconds)
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(window_seconds)
    
    return response


def get_rate_limit_config(path: str) -> Tuple[int, int]:
    """
    Get rate limit configuration for specific path.
    
    Args:
        path: Request path
        
    Returns:
        Tuple of (max_requests, window_seconds)
    """
    # Stricter limits for auth endpoints
    if "/auth/login" in path:
        return (5, 60)  # 5 requests per minute
    elif "/auth/register" in path:
        return (3, 60)  # 3 requests per minute
    elif "/api/v1/claims" in path:
        return (50, 60)  # 50 requests per minute
    else:
        return (100, 60)  # Default: 100 requests per minute

