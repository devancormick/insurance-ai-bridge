"""SOAP API client for legacy system."""
from typing import Dict, Any
from app.config import settings


class SOAPClient:
    """Client for SOAP API integration."""
    
    def __init__(self):
        """Initialize SOAP client."""
        self.api_url = settings.soap_api_url
    
    async def get_claim_details(self, claim_id: str) -> Dict[str, Any]:
        """Get claim details from SOAP API."""
        # TODO: Implement SOAP client
        return {}
    
    async def get_policy_info(self, policy_id: str) -> Dict[str, Any]:
        """Get policy information from SOAP API."""
        # TODO: Implement SOAP client
        return {}

