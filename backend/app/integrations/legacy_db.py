"""Legacy database integration."""
from typing import Dict, Any, List
from app.config import settings


class LegacyDBClient:
    """Client for connecting to legacy SQL Server database."""
    
    def __init__(self):
        """Initialize legacy database client."""
        self.host = settings.legacy_db_host
        self.port = settings.legacy_db_port
        self.database = settings.legacy_db_name
        self.user = settings.legacy_db_user
        self.password = settings.legacy_db_password
    
    async def get_claim_data(self, claim_id: str) -> Dict[str, Any]:
        """Retrieve claim data from legacy database."""
        # TODO: Implement SQL Server connection and query
        return {}
    
    async def get_member_data(self, member_id: str) -> Dict[str, Any]:
        """Retrieve member data from legacy database."""
        # TODO: Implement SQL Server connection and query
        return {}
    
    async def get_policy_data(self, policy_id: str) -> Dict[str, Any]:
        """Retrieve policy data from legacy database."""
        # TODO: Implement SQL Server connection and query
        return {}

