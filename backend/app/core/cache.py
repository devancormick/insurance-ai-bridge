"""Redis caching layer."""
from typing import Optional, Any
import json
import asyncio
from app.config import settings
from app.utils.logging import logger


class Cache:
    """Redis cache wrapper with fallback to in-memory cache."""
    
    def __init__(self):
        """Initialize cache client."""
        self.redis_client: Optional[Any] = None
        self.in_memory_cache: dict = {}
        self._is_redis_available = False
        
        # Try to initialize Redis
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self._is_redis_available = True
            logger.info("Redis cache initialized")
        except ImportError:
            logger.warning("Redis not installed, using in-memory cache")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}, using in-memory cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if self._is_redis_available and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
            except Exception as e:
                logger.error(f"Error getting from Redis cache: {e}")
        
        # Fallback to in-memory cache
        if key in self.in_memory_cache:
            value, expiry = self.in_memory_cache[key]
            if expiry is None or expiry > asyncio.get_event_loop().time():
                return value
            else:
                del self.in_memory_cache[key]
        
        return None
    
    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
            
        Returns:
            True if successful
        """
        serialized_value = json.dumps(value) if not isinstance(value, str) else value
        
        if self._is_redis_available and self.redis_client:
            try:
                if ttl:
                    await self.redis_client.setex(key, ttl, serialized_value)
                else:
                    await self.redis_client.set(key, serialized_value)
                return True
            except Exception as e:
                logger.error(f"Error setting Redis cache: {e}")
        
        # Fallback to in-memory cache
        expiry = None
        if ttl:
            expiry = asyncio.get_event_loop().time() + ttl
        self.in_memory_cache[key] = (value, expiry)
        
        # Cleanup old entries periodically
        if len(self.in_memory_cache) > 1000:
            self._cleanup_in_memory_cache()
        
        return True
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if self._is_redis_available and self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Error deleting from Redis cache: {e}")
        
        # Remove from in-memory cache
        if key in self.in_memory_cache:
            del self.in_memory_cache[key]
            return True
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "claims:*")
            
        Returns:
            Number of keys deleted
        """
        if self._is_redis_available and self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    return await self.redis_client.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Error clearing Redis cache pattern: {e}")
                return 0
        
        # Fallback: clear matching keys from in-memory cache
        deleted = 0
        keys_to_delete = [k for k in self.in_memory_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self.in_memory_cache[key]
            deleted += 1
        
        return deleted
    
    def _cleanup_in_memory_cache(self):
        """Remove expired entries from in-memory cache."""
        current_time = asyncio.get_event_loop().time()
        expired_keys = [
            key for key, (_, expiry) in self.in_memory_cache.items()
            if expiry is not None and expiry <= current_time
        ]
        for key in expired_keys:
            del self.in_memory_cache[key]
    
    async def close(self):
        """Close cache connections."""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")


# Global cache instance
cache = Cache()

