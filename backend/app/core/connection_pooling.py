"""
Advanced Connection Pooling
PgBouncer integration and connection pool management
"""

from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """Manages database connection pools"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.primary_pool = None
        self.read_replica_pools = {}
        self.pooler_url = config.get("pooler_url")  # PgBouncer URL
        self.direct_url = config.get("direct_url")  # Direct PostgreSQL URL
        self.pool_size = config.get("pool_size", 20)
        self.max_overflow = config.get("max_overflow", 10)
        self.pool_timeout = config.get("pool_timeout", 30)
        self.pool_recycle = config.get("pool_recycle", 3600)
        self.read_replicas = config.get("read_replicas", [])
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Initialize connection pools"""
        # Primary pool (write operations)
        if self.pooler_url:
            # Use PgBouncer for connection pooling
            self.primary_pool = create_async_engine(
                self.pooler_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=False,
                future=True
            )
            logger.info(f"Initialized primary connection pool with PgBouncer: pool_size={self.pool_size}")
        else:
            # Direct connection pool
            self.primary_pool = create_async_engine(
                self.direct_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=False,
                future=True
            )
            logger.info(f"Initialized primary connection pool: pool_size={self.pool_size}")
        
        # Read replica pools
        for replica_config in self.read_replicas:
            replica_name = replica_config.get("name", "replica")
            replica_url = replica_config.get("url")
            
            if replica_url:
                self.read_replica_pools[replica_name] = create_async_engine(
                    replica_url,
                    poolclass=QueuePool,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_timeout=self.pool_timeout,
                    pool_recycle=self.pool_recycle,
                    echo=False,
                    future=True
                )
                logger.info(f"Initialized read replica pool '{replica_name}': pool_size={self.pool_size}")
    
    @asynccontextmanager
    async def get_write_session(self):
        """Get a write session from primary pool"""
        async_session = async_sessionmaker(
            self.primary_pool,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_read_session(self, replica_name: Optional[str] = None):
        """Get a read session from read replica pool"""
        if replica_name and replica_name in self.read_replica_pools:
            pool = self.read_replica_pools[replica_name]
        elif self.read_replica_pools:
            # Use first available replica
            pool = next(iter(self.read_replica_pools.values()))
        else:
            # Fallback to primary pool for reads
            pool = self.primary_pool
        
        async_session = async_sessionmaker(
            pool,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        stats = {
            "primary_pool": {
                "size": self.primary_pool.pool.size() if self.primary_pool else 0,
                "checked_in": self.primary_pool.pool.checkedin() if self.primary_pool else 0,
                "checked_out": self.primary_pool.pool.checkedout() if self.primary_pool else 0,
                "overflow": self.primary_pool.pool.overflow() if self.primary_pool else 0,
            },
            "read_replicas": {}
        }
        
        for replica_name, pool in self.read_replica_pools.items():
            stats["read_replicas"][replica_name] = {
                "size": pool.pool.size() if pool else 0,
                "checked_in": pool.pool.checkedin() if pool else 0,
                "checked_out": pool.pool.checkedout() if pool else 0,
                "overflow": pool.pool.overflow() if pool else 0,
            }
        
        return stats
    
    async def close_all(self):
        """Close all connection pools"""
        if self.primary_pool:
            await self.primary_pool.dispose()
        
        for pool in self.read_replica_pools.values():
            await pool.dispose()
        
        logger.info("All connection pools closed")


# Global connection pool manager
connection_pool_manager: Optional[ConnectionPoolManager] = None


def get_connection_pool_manager() -> ConnectionPoolManager:
    """Get the global connection pool manager"""
    global connection_pool_manager
    if connection_pool_manager is None:
        from app.config import settings
        connection_pool_manager = ConnectionPoolManager(settings.database_pool_config)
    return connection_pool_manager

