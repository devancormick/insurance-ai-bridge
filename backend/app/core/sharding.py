"""
Database Sharding Logic
Implements sharding strategies for horizontal scaling
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import hashlib
import logging

logger = logging.getLogger(__name__)


class ShardingStrategy(Enum):
    """Sharding strategy types"""
    RANGE = "range"           # Shard by value ranges
    HASH = "hash"             # Shard by hash function
    DIRECTORY = "directory"   # Shard by lookup table
    GEOGRAPHIC = "geographic" # Shard by geographic location
    TENANT = "tenant"         # Shard by tenant ID


@dataclass
class Shard:
    """Represents a database shard"""
    shard_id: str
    shard_key: str
    database_url: str
    region: Optional[str] = None
    capacity: Optional[int] = None
    active: bool = True


class ShardManager:
    """Manages database sharding"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.shards: Dict[str, List[Shard]] = {}
        self.strategy = ShardingStrategy(config.get("strategy", "hash"))
        self.num_shards = config.get("num_shards", 4)
        self.shard_key_field = config.get("shard_key_field", "member_id")
        self._initialize_shards()
    
    def _initialize_shards(self):
        """Initialize shards from configuration"""
        shard_configs = self.config.get("shards", [])
        
        for table_name in self.config.get("sharded_tables", ["claims", "members"]):
            self.shards[table_name] = []
            
            for shard_config in shard_configs:
                shard = Shard(
                    shard_id=shard_config["shard_id"],
                    shard_key=shard_config.get("shard_key", ""),
                    database_url=shard_config["database_url"],
                    region=shard_config.get("region"),
                    capacity=shard_config.get("capacity"),
                    active=shard_config.get("active", True)
                )
                self.shards[table_name].append(shard)
        
        if not shard_configs:
            # Create default shards if none configured
            self._create_default_shards()
    
    def _create_default_shards(self):
        """Create default shard configuration"""
        for table_name in self.config.get("sharded_tables", ["claims"]):
            self.shards[table_name] = []
            
            for i in range(self.num_shards):
                shard = Shard(
                    shard_id=f"shard_{i}",
                    shard_key=f"shard_{i}",
                    database_url=f"postgresql://shard-{i}.db.internal/insurance_ai_bridge",
                    region=None,
                    active=True
                )
                self.shards[table_name].append(shard)
    
    def get_shard(self, table_name: str, shard_key_value: Any) -> Optional[Shard]:
        """
        Get the shard for a given table and shard key value
        
        Args:
            table_name: Name of the table
            shard_key_value: Value of the shard key field
        
        Returns:
            Shard object or None if not found
        """
        if table_name not in self.shards:
            logger.warning(f"Table {table_name} is not sharded")
            return None
        
        available_shards = [s for s in self.shards[table_name] if s.active]
        
        if not available_shards:
            logger.error(f"No active shards available for table {table_name}")
            return None
        
        if self.strategy == ShardingStrategy.HASH:
            return self._get_shard_by_hash(available_shards, shard_key_value)
        elif self.strategy == ShardingStrategy.RANGE:
            return self._get_shard_by_range(available_shards, shard_key_value)
        elif self.strategy == ShardingStrategy.DIRECTORY:
            return self._get_shard_by_directory(available_shards, shard_key_value)
        elif self.strategy == ShardingStrategy.GEOGRAPHIC:
            return self._get_shard_by_geographic(available_shards, shard_key_value)
        elif self.strategy == ShardingStrategy.TENANT:
            return self._get_shard_by_tenant(available_shards, shard_key_value)
        else:
            # Default to round-robin
            return available_shards[hash(str(shard_key_value)) % len(available_shards)]
    
    def _get_shard_by_hash(self, shards: List[Shard], key_value: Any) -> Shard:
        """Get shard using hash function"""
        key_str = str(key_value)
        hash_value = int(hashlib.md5(key_str.encode()).hexdigest(), 16)
        shard_index = hash_value % len(shards)
        return shards[shard_index]
    
    def _get_shard_by_range(self, shards: List[Shard], key_value: Any) -> Shard:
        """Get shard using range-based lookup"""
        # This would use a range map from config
        # Simplified implementation - assumes numeric key and even distribution
        if isinstance(key_value, (int, float)):
            shard_index = int(key_value) % len(shards)
            return shards[shard_index]
        else:
            # Fallback to hash for non-numeric keys
            return self._get_shard_by_hash(shards, key_value)
    
    def _get_shard_by_directory(self, shards: List[Shard], key_value: Any) -> Shard:
        """Get shard using directory/lookup table"""
        # This would query a lookup table
        # Simplified - use hash as fallback
        return self._get_shard_by_hash(shards, key_value)
    
    def _get_shard_by_geographic(self, shards: List[Shard], key_value: Any) -> Shard:
        """Get shard based on geographic location"""
        # This would use geo-location data
        # Simplified - use hash as fallback
        return self._get_shard_by_hash(shards, key_value)
    
    def _get_shard_by_tenant(self, shards: List[Shard], key_value: Any) -> Shard:
        """Get shard based on tenant ID"""
        # Tenant-based sharding (similar to hash but with tenant isolation)
        return self._get_shard_by_hash(shards, key_value)
    
    def get_all_shards(self, table_name: str) -> List[Shard]:
        """Get all shards for a table"""
        return self.shards.get(table_name, [])
    
    def add_shard(self, table_name: str, shard: Shard):
        """Add a new shard"""
        if table_name not in self.shards:
            self.shards[table_name] = []
        self.shards[table_name].append(shard)
        logger.info(f"Added shard {shard.shard_id} for table {table_name}")
    
    def remove_shard(self, table_name: str, shard_id: str):
        """Remove a shard (mark as inactive)"""
        if table_name in self.shards:
            for shard in self.shards[table_name]:
                if shard.shard_id == shard_id:
                    shard.active = False
                    logger.info(f"Removed shard {shard_id} for table {table_name}")
                    return
        logger.warning(f"Shard {shard_id} not found for table {table_name}")
    
    def get_shard_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get statistics about shards for a table"""
        if table_name not in self.shards:
            return {"error": f"Table {table_name} is not sharded"}
        
        shards = self.shards[table_name]
        active_shards = [s for s in shards if s.active]
        
        return {
            "total_shards": len(shards),
            "active_shards": len(active_shards),
            "inactive_shards": len(shards) - len(active_shards),
            "shards": [
                {
                    "shard_id": s.shard_id,
                    "region": s.region,
                    "active": s.active,
                    "capacity": s.capacity
                }
                for s in shards
            ]
        }


class CrossShardQuery:
    """Handles queries that span multiple shards"""
    
    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager
    
    async def execute_cross_shard_query(
        self,
        table_name: str,
        query_func,
        aggregator_func=None
    ) -> List[Any]:
        """
        Execute a query across all shards and aggregate results
        
        Args:
            table_name: Table to query
            query_func: Async function that executes query on a shard, returns results
            aggregator_func: Optional function to aggregate results from all shards
        
        Returns:
            Aggregated results from all shards
        """
        shards = self.shard_manager.get_all_shards(table_name)
        active_shards = [s for s in shards if s.active]
        
        results = []
        
        # Execute query on each shard in parallel (would use asyncio.gather in real implementation)
        for shard in active_shards:
            try:
                shard_results = await query_func(shard)
                results.extend(shard_results)
            except Exception as e:
                logger.error(f"Error querying shard {shard.shard_id}: {e}", exc_info=True)
        
        # Aggregate results if aggregator function provided
        if aggregator_func:
            return aggregator_func(results)
        
        return results
    
    async def execute_aggregation_query(
        self,
        table_name: str,
        aggregation_func,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute aggregation query across shards
        
        Args:
            table_name: Table to aggregate
            aggregation_func: Function to perform aggregation on each shard
            group_by: Optional field to group by
        
        Returns:
            Aggregated results
        """
        shards = self.shard_manager.get_all_shards(table_name)
        active_shards = [s for s in shards if s.active]
        
        shard_results = []
        
        for shard in active_shards:
            try:
                result = await aggregation_func(shard)
                shard_results.append(result)
            except Exception as e:
                logger.error(f"Error aggregating shard {shard.shard_id}: {e}", exc_info=True)
        
        # Combine results from all shards
        # For aggregations like SUM, COUNT, AVG, we combine shard-level results
        combined_result = self._combine_aggregation_results(shard_results, group_by)
        
        return combined_result
    
    def _combine_aggregation_results(self, shard_results: List[Dict[str, Any]], group_by: Optional[str]) -> Dict[str, Any]:
        """Combine aggregation results from multiple shards"""
        if not shard_results:
            return {}
        
        if group_by:
            # Grouped aggregation - merge groups from all shards
            combined = {}
            for result in shard_results:
                for group_key, group_value in result.items():
                    if group_key not in combined:
                        combined[group_key] = group_value
                    else:
                        # Merge aggregated values (for SUM, COUNT, etc.)
                        combined[group_key] = self._merge_group_values(combined[group_key], group_value)
            return combined
        else:
            # Simple aggregation - combine values
            return self._merge_group_values(*shard_results)
    
    def _merge_group_values(self, *values: Dict[str, Any]) -> Dict[str, Any]:
        """Merge aggregated values from multiple groups"""
        merged = {}
        for value_dict in values:
            for key, val in value_dict.items():
                if key not in merged:
                    merged[key] = val
                elif isinstance(val, (int, float)) and isinstance(merged[key], (int, float)):
                    merged[key] += val  # Sum aggregation
                elif isinstance(val, list):
                    merged[key] = (merged.get(key, []) + val)
        return merged


# Global shard manager instance
shard_manager: Optional[ShardManager] = None


def get_shard_manager() -> ShardManager:
    """Get the global shard manager instance"""
    global shard_manager
    if shard_manager is None:
        from app.config import settings
        shard_manager = ShardManager(settings.sharding_config)
    return shard_manager

