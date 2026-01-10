"""Async Redis client wrapper."""
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings
from app.utils.logging import logger


class AsyncRedisClient:
    """Async Redis client with connection pooling."""
    
    def __init__(self):
        """Initialize Redis client."""
        self.client: Optional[redis.Redis] = None
        self._is_available = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Test connection
            await self.client.ping()
            self._is_available = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}, using in-memory fallback")
            self._is_available = False
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            try:
                await self.client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._is_available
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._is_available or not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in Redis."""
        if not self._is_available or not self.client:
            return False
        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self._is_available or not self.client:
            return False
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

