"""
Multi-Tier Caching Strategy
L1 (in-memory), L2 (Redis), L3 (CDN) with intelligent invalidation
"""

from typing import Optional, Any, Dict, List
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import logging


logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """Cache tier levels"""
    L1 = "l1"  # In-memory cache
    L2 = "l2"  # Redis cache
    L3 = "l3"  # CDN cache


class CacheStrategy:
    """Multi-tier caching strategy manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.l1_cache: Dict[str, Any] = {}  # In-memory cache
        self.l2_redis = None  # Redis client (to be initialized)
        self.l3_cdn = None  # CDN client (to be initialized)
        self.cache_dependencies: Dict[str, List[str]] = {}  # Dependency tracking
    
    async def get(self, key: str, tier: Optional[CacheTier] = None) -> Optional[Any]:
        """
        Get value from cache with tier priority
        
        Args:
            key: Cache key
            tier: Specific tier to check (None = check all tiers)
        
        Returns:
            Cached value or None
        """
        # Check L1 (in-memory) first
        if tier is None or tier == CacheTier.L1:
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if entry.get("expires_at") > datetime.utcnow():
                    logger.debug(f"Cache HIT L1: {key}")
                    return entry.get("value")
                else:
                    del self.l1_cache[key]
        
        # Check L2 (Redis) second
        if tier is None or tier == CacheTier.L2:
            if self.l2_redis:
                value = await self._get_from_redis(key)
                if value is not None:
                    logger.debug(f"Cache HIT L2: {key}")
                    # Promote to L1
                    await self.set(key, value, tier=CacheTier.L1)
                    return value
        
        # Check L3 (CDN) last
        if tier is None or tier == CacheTier.L3:
            if self.l3_cdn:
                value = await self._get_from_cdn(key)
                if value is not None:
                    logger.debug(f"Cache HIT L3: {key}")
                    # Promote to L1 and L2
                    await self.set(key, value, tier=CacheTier.L1)
                    await self.set(key, value, tier=CacheTier.L2)
                    return value
        
        logger.debug(f"Cache MISS: {key}")
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        tier: Optional[CacheTier] = None,
        dependencies: Optional[List[str]] = None
    ):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tier: Specific tier to set (None = set in all tiers)
            dependencies: List of dependent cache keys
        """
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        cache_entry = {"value": value, "expires_at": expires_at}
        
        # Set in L1 (in-memory)
        if tier is None or tier == CacheTier.L1:
            self.l1_cache[key] = cache_entry
        
        # Set in L2 (Redis)
        if (tier is None or tier == CacheTier.L2) and self.l2_redis:
            await self._set_in_redis(key, value, ttl)
        
        # Set in L3 (CDN) - typically for static assets
        if (tier is None or tier == CacheTier.L3) and self.l3_cdn:
            await self._set_in_cdn(key, value, ttl)
        
        # Track dependencies
        if dependencies:
            self.cache_dependencies[key] = dependencies
        
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    async def invalidate(self, key: str, cascade: bool = True):
        """
        Invalidate cache key and dependent keys
        
        Args:
            key: Cache key to invalidate
            cascade: Whether to invalidate dependent keys
        """
        # Invalidate L1
        if key in self.l1_cache:
            del self.l1_cache[key]
            logger.debug(f"Cache INVALIDATED L1: {key}")
        
        # Invalidate L2
        if self.l2_redis:
            await self._invalidate_redis(key)
            logger.debug(f"Cache INVALIDATED L2: {key}")
        
        # Invalidate L3
        if self.l3_cdn:
            await self._invalidate_cdn(key)
            logger.debug(f"Cache INVALIDATED L3: {key}")
        
        # Cascade invalidation to dependent keys
        if cascade:
            dependent_keys = self.cache_dependencies.get(key, [])
            for dep_key in dependent_keys:
                await self.invalidate(dep_key, cascade=False)
    
    async def warm_cache(self, keys: List[str], loader: callable):
        """
        Warm cache by preloading keys
        
        Args:
            keys: List of keys to warm
            loader: Async function to load values for keys
        """
        logger.info(f"Warming cache for {len(keys)} keys")
        
        for key in keys:
            try:
                value = await loader(key)
                if value is not None:
                    await self.set(key, value, ttl=3600)
            except Exception as e:
                logger.error(f"Error warming cache for {key}: {e}")
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        # Placeholder - real implementation would use redis.asyncio
        return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int):
        """Set value in Redis"""
        # Placeholder - real implementation would use redis.asyncio
        pass
    
    async def _invalidate_redis(self, key: str):
        """Invalidate key in Redis"""
        # Placeholder - real implementation would use redis.asyncio
        pass
    
    async def _get_from_cdn(self, key: str) -> Optional[Any]:
        """Get value from CDN"""
        # Placeholder - real implementation would use CDN API
        return None
    
    async def _set_in_cdn(self, key: str, value: Any, ttl: int):
        """Set value in CDN"""
        # Placeholder - real implementation would use CDN API
        pass
    
    async def _invalidate_cdn(self, key: str):
        """Invalidate key in CDN"""
        # Placeholder - real implementation would use CDN API
        pass
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate consistent cache key from parameters
        
        Args:
            prefix: Cache key prefix
            **kwargs: Parameters to include in key
        
        Returns:
            Generated cache key
        """
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"


# Global cache strategy instance
cache_strategy: Optional[CacheStrategy] = None


def get_cache_strategy() -> CacheStrategy:
    """Get global cache strategy instance"""
    global cache_strategy
    if cache_strategy is None:
        from app.config import settings
        cache_strategy = CacheStrategy(settings.cache_config)
    return cache_strategy

