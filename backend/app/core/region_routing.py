"""
Region-Aware Routing Logic
Routes requests to appropriate regions based on location, load, and health
"""

from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class Region(Enum):
    """Available regions"""
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"


@dataclass
class RegionHealth:
    """Region health status"""
    region: Region
    healthy: bool
    latency_ms: float
    error_rate: float
    load_percentage: float
    last_updated: datetime


class RegionRouter:
    """Region-aware routing manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.regions = config.get("regions", [r.value for r in Region])
        self.region_health: Dict[str, RegionHealth] = {}
        self.default_region = config.get("default_region", Region.US_EAST.value)
    
    def get_region_for_request(
        self,
        client_ip: Optional[str] = None,
        user_region: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> str:
        """
        Determine best region for request
        
        Args:
            client_ip: Client IP address for geo-routing
            user_region: User's preferred region
            resource_type: Type of resource being accessed
        
        Returns:
            Best region identifier
        """
        # User preference takes priority
        if user_region and user_region in self.regions:
            if self._is_region_healthy(user_region):
                return user_region
        
        # Geo-routing based on client IP
        if client_ip:
            geo_region = self._get_region_from_ip(client_ip)
            if geo_region and self._is_region_healthy(geo_region):
                return geo_region
        
        # Resource-specific routing
        if resource_type:
            resource_region = self._get_region_for_resource(resource_type)
            if resource_region and self._is_region_healthy(resource_region):
                return resource_region
        
        # Fallback to least loaded healthy region
        return self._get_least_loaded_region()
    
    def _is_region_healthy(self, region: str) -> bool:
        """Check if region is healthy"""
        health = self.region_health.get(region)
        if not health:
            return True  # Assume healthy if no data
        
        return health.healthy and health.error_rate < 0.1
    
    def _get_region_from_ip(self, client_ip: str) -> Optional[str]:
        """Get region from client IP using geo-location"""
        # Placeholder - real implementation would use MaxMind GeoIP or similar
        # Simple heuristic based on IP ranges
        if client_ip.startswith("54.") or client_ip.startswith("52."):
            return Region.US_EAST.value
        elif client_ip.startswith("54.") or client_ip.startswith("52."):
            return Region.US_WEST.value
        elif client_ip.startswith("52.") or client_ip.startswith("51."):
            return Region.EU_WEST.value
        return None
    
    def _get_region_for_resource(self, resource_type: str) -> Optional[str]:
        """Get preferred region for resource type"""
        # Placeholder - could route based on data locality
        resource_region_map = self.config.get("resource_regions", {})
        return resource_region_map.get(resource_type)
    
    def _get_least_loaded_region(self) -> str:
        """Get least loaded healthy region"""
        healthy_regions = [
            (region, health) for region, health in self.region_health.items()
            if health and health.healthy
        ]
        
        if not healthy_regions:
            return self.default_region
        
        # Sort by load percentage
        healthy_regions.sort(key=lambda x: x[1].load_percentage)
        return healthy_regions[0][0]
    
    def update_region_health(self, region: str, health: RegionHealth):
        """Update region health status"""
        self.region_health[region] = health

