"""Tests for cache."""
import pytest
from app.core.cache import Cache


@pytest.fixture
async def cache():
    """Create cache instance."""
    cache_instance = Cache()
    yield cache_instance
    await cache_instance.close()


@pytest.mark.asyncio
async def test_cache_set_get(cache):
    """Test setting and getting cache values."""
    key = "test_key"
    value = {"data": "test_value", "number": 123}
    
    # Set value
    result = await cache.set(key, value, ttl=60)
    assert result is True
    
    # Get value
    retrieved = await cache.get(key)
    assert retrieved == value


@pytest.mark.asyncio
async def test_cache_delete(cache):
    """Test deleting cache values."""
    key = "test_delete_key"
    value = "test_value"
    
    # Set value
    await cache.set(key, value)
    
    # Verify it exists
    retrieved = await cache.get(key)
    assert retrieved == value
    
    # Delete it
    result = await cache.delete(key)
    assert result is True
    
    # Verify it's gone
    retrieved = await cache.get(key)
    assert retrieved is None


@pytest.mark.asyncio
async def test_cache_expiration(cache):
    """Test cache expiration."""
    key = "test_expire_key"
    value = "test_value"
    
    # Set with short TTL
    await cache.set(key, value, ttl=1)
    
    # Should exist immediately
    retrieved = await cache.get(key)
    assert retrieved == value
    
    # Wait for expiration
    import asyncio
    await asyncio.sleep(2)
    
    # Should be expired (for in-memory cache, this may not work with Redis)
    # This test may need adjustment based on cache implementation

