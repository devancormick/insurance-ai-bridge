"""
Data Tiering Logic
Implements multi-tier data strategy: Hot (Cloud), Warm (Hybrid), Cold (On-Premise)
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass


class DataTier(Enum):
    """Data tier classification"""
    HOT = "hot"      # Recent claims (last 90 days), frequently accessed
    WARM = "warm"    # Claims 90-365 days old, replicated to both tiers
    COLD = "cold"    # Archive data (>1 year), compliance records, audit logs
    METADATA = "metadata"  # User data, policy metadata synchronized across tiers


@dataclass
class DataTieringRule:
    """Data tiering rule configuration"""
    tier: DataTier
    age_days: Optional[int] = None
    access_frequency: Optional[str] = None
    data_type: Optional[str] = None
    replication_required: bool = False


class DataTieringManager:
    """Manages data tiering and routing logic"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tiering_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> list[DataTieringRule]:
        """Initialize data tiering rules"""
        return [
            DataTieringRule(
                tier=DataTier.HOT,
                age_days=90,
                access_frequency="high",
                data_type="claim",
                replication_required=False
            ),
            DataTieringRule(
                tier=DataTier.WARM,
                age_days=365,
                access_frequency="medium",
                data_type="claim",
                replication_required=True
            ),
            DataTieringRule(
                tier=DataTier.COLD,
                age_days=365,
                access_frequency="low",
                data_type="archive",
                replication_required=False
            ),
            DataTieringRule(
                tier=DataTier.METADATA,
                data_type="metadata",
                replication_required=True
            )
        ]
    
    def determine_tier(self, created_at: datetime, access_count: int = 0, data_type: str = "claim") -> DataTier:
        """
        Determine the appropriate tier for data based on age, access frequency, and type
        
        Args:
            created_at: When the data was created
            access_count: Number of times accessed (for frequency calculation)
            data_type: Type of data (claim, metadata, archive, etc.)
        
        Returns:
            DataTier classification
        """
        age_days = (datetime.utcnow() - created_at).days
        
        # Metadata always goes to metadata tier
        if data_type == "metadata":
            return DataTier.METADATA
        
        # Archive data goes to cold tier
        if data_type == "archive":
            return DataTier.COLD
        
        # Hot tier: recent and frequently accessed
        if age_days <= 90 and access_count > 10:
            return DataTier.HOT
        
        # Warm tier: medium age (90-365 days) or medium access
        if 90 < age_days <= 365 or (age_days <= 365 and 5 < access_count <= 10):
            return DataTier.WARM
        
        # Cold tier: old data (>1 year)
        if age_days > 365:
            return DataTier.COLD
        
        # Default to hot for new data
        return DataTier.HOT
    
    def get_storage_location(self, tier: DataTier, region: Optional[str] = None) -> str:
        """
        Get the storage location for a given tier
        
        Args:
            tier: Data tier classification
            region: Optional region for routing
        
        Returns:
            Storage location endpoint or identifier
        """
        tier_config = self.config.get("tiers", {}).get(tier.value, {})
        
        if tier == DataTier.HOT:
            # Cloud storage (AWS S3, Azure Blob, etc.)
            return tier_config.get("cloud_storage", "s3://insurance-ai-bridge-hot")
        
        elif tier == DataTier.WARM:
            # Hybrid storage (replicated to both cloud and on-premise)
            return tier_config.get("hybrid_storage", "hybrid://insurance-ai-bridge-warm")
        
        elif tier == DataTier.COLD:
            # On-premise storage for compliance
            return tier_config.get("onprem_storage", "onprem://insurance-ai-bridge-cold")
        
        elif tier == DataTier.METADATA:
            # Synchronized across both tiers
            return tier_config.get("metadata_storage", "sync://insurance-ai-bridge-metadata")
        
        return "unknown"
    
    def should_replicate(self, tier: DataTier) -> bool:
        """Check if data in this tier should be replicated"""
        for rule in self.tiering_rules:
            if rule.tier == tier:
                return rule.replication_required
        return False
    
    def get_migration_candidates(self, source_tier: DataTier, target_tier: DataTier, age_threshold_days: int) -> list:
        """
        Get candidates for migration between tiers
        
        Args:
            source_tier: Current tier
            target_tier: Target tier
            age_threshold_days: Age threshold for migration
        
        Returns:
            List of data identifiers to migrate
        """
        # This would query the database for candidates
        # Placeholder implementation
        cutoff_date = datetime.utcnow() - timedelta(days=age_threshold_days)
        return []  # Would return list of IDs from database query
    
    def calculate_tier_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for each tier"""
        # Placeholder for statistics calculation
        return {
            "hot": {"count": 0, "size_gb": 0},
            "warm": {"count": 0, "size_gb": 0},
            "cold": {"count": 0, "size_gb": 0},
            "metadata": {"count": 0, "size_gb": 0}
        }


# Global instance (to be initialized with config)
data_tiering_manager: Optional[DataTieringManager] = None


def get_tiering_manager() -> DataTieringManager:
    """Get the global data tiering manager instance"""
    global data_tiering_manager
    if data_tiering_manager is None:
        from app.config import settings
        data_tiering_manager = DataTieringManager(settings.data_tiering_config)
    return data_tiering_manager

