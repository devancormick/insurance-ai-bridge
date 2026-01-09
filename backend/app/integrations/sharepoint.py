"""SharePoint document integration."""
from typing import List, Dict, Any
from app.config import settings


class SharePointClient:
    """Client for SharePoint document retrieval."""
    
    def __init__(self):
        """Initialize SharePoint client."""
        self.sharepoint_url = settings.sharepoint_url
        self.client_id = settings.sharepoint_client_id
        self.client_secret = settings.sharepoint_client_secret
    
    async def get_policy_documents(self, policy_id: str) -> List[Dict[str, Any]]:
        """Retrieve policy documents from SharePoint."""
        # TODO: Implement SharePoint integration
        return []
    
    async def get_claim_documents(self, claim_id: str) -> List[Dict[str, Any]]:
        """Retrieve claim-related documents from SharePoint."""
        # TODO: Implement SharePoint integration
        return []

