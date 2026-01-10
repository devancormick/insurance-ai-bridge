"""Tests for rate limiter."""
import pytest
from app.core.rate_limiter import RateLimiter


@pytest.fixture
def rate_limiter():
    """Create rate limiter instance."""
    return RateLimiter()


def test_rate_limit_allowed(rate_limiter):
    """Test that requests within limit are allowed."""
    key = "test_key"
    max_requests = 5
    window = 60
    
    # Make 5 requests (within limit)
    for i in range(5):
        is_allowed, remaining = rate_limiter.is_allowed(key, max_requests, window)
        assert is_allowed is True
        assert remaining == (max_requests - i - 1)


def test_rate_limit_exceeded(rate_limiter):
    """Test that requests exceeding limit are denied."""
    key = "test_key_limit"
    max_requests = 3
    window = 60
    
    # Make requests within limit
    for i in range(3):
        is_allowed, remaining = rate_limiter.is_allowed(key, max_requests, window)
        assert is_allowed is True
    
    # Next request should be denied
    is_allowed, remaining = rate_limiter.is_allowed(key, max_requests, window)
    assert is_allowed is False
    assert remaining == 0


def test_rate_limit_different_keys(rate_limiter):
    """Test that different keys have independent rate limits."""
    key1 = "key1"
    key2 = "key2"
    max_requests = 3
    window = 60
    
    # Exhaust limit for key1
    for _ in range(3):
        rate_limiter.is_allowed(key1, max_requests, window)
    
    # key2 should still have full limit
    is_allowed, remaining = rate_limiter.is_allowed(key2, max_requests, window)
    assert is_allowed is True
    assert remaining == 2

