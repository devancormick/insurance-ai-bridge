"""Data aggregation from multiple sources."""
from typing import Dict, Any, List, Optional
from app.utils.logging import logger


class DataAggregator:
    """Aggregates data from multiple legacy sources."""
    
    def __init__(self):
        """Initialize data aggregator with integration clients."""
        self.db_client: Optional[Any] = None
        self.soap_client: Optional[Any] = None
        self.sharepoint_client: Optional[Any] = None
        
        # Lazy initialization of clients
        try:
            from app.integrations.legacy_db import LegacyDBClient
            self.db_client = LegacyDBClient()
        except Exception as e:
            logger.warning(f"Could not initialize LegacyDBClient: {e}")
        
        try:
            from app.integrations.soap_client import SOAPClient
            self.soap_client = SOAPClient()
        except Exception as e:
            logger.warning(f"Could not initialize SOAPClient: {e}")
        
        try:
            from app.integrations.sharepoint import SharePointClient
            self.sharepoint_client = SharePointClient()
        except Exception as e:
            logger.warning(f"Could not initialize SharePointClient: {e}")
    
    async def get_claim_context(
        self, claim_id: str, include_history: bool = True, include_docs: bool = True
    ) -> Dict[str, Any]:
        """
        Aggregate all context for a claim.
        
        Args:
            claim_id: Unique claim identifier
            include_history: Include member claim history
            include_docs: Include policy documents
            
        Returns:
            Dictionary with aggregated claim context
        """
        from app.utils.logging import logger
        
        context = {
            "claim_id": claim_id,
            "claim_data": {},
            "member_data": {},
            "policy_data": {},
            "documents": [],
        }
        
        logger.info(f"Aggregating context for claim {claim_id}")
        
        # Fetch claim data from legacy database
        if self.db_client:
            try:
                claim_data = await self.db_client.get_claim_data(claim_id)
                context["claim_data"] = claim_data
                
                # Extract member_id and policy_id from claim data
                member_id = claim_data.get("member_id") or claim_data.get("MemberID")
                policy_id = claim_data.get("policy_id") or claim_data.get("PolicyID")
                
                # Fetch member data if available
                if member_id and include_history:
                    try:
                        member_data = await self.db_client.get_member_data(member_id)
                        context["member_data"] = member_data
                    except Exception as e:
                        logger.warning(f"Could not fetch member data for {member_id}: {e}")
                
                # Fetch policy data if available
                if policy_id:
                    try:
                        policy_data = await self.db_client.get_policy_data(policy_id)
                        context["policy_data"] = policy_data
                        
                        # Fetch policy documents if requested
                        if include_docs and self.sharepoint_client:
                            try:
                                documents = await self.sharepoint_client.get_policy_documents(policy_id)
                                context["documents"].extend(documents)
                            except Exception as e:
                                logger.warning(f"Could not fetch policy documents: {e}")
                    except Exception as e:
                        logger.warning(f"Could not fetch policy data for {policy_id}: {e}")
            except Exception as e:
                logger.error(f"Error fetching claim data from legacy DB: {e}")
        
        # Fetch additional claim details from SOAP API
        if self.soap_client:
            try:
                soap_claim_data = await self.soap_client.get_claim_details(claim_id)
                # Merge SOAP data into claim_data
                if soap_claim_data:
                    context["claim_data"].update(soap_claim_data)
            except Exception as e:
                logger.warning(f"Could not fetch claim details from SOAP API: {e}")
        
        # Fetch claim-specific documents from SharePoint
        if include_docs and self.sharepoint_client:
            try:
                claim_docs = await self.sharepoint_client.get_claim_documents(claim_id)
                context["documents"].extend(claim_docs)
            except Exception as e:
                logger.warning(f"Could not fetch claim documents from SharePoint: {e}")
        
        logger.info(f"Context aggregation complete for claim {claim_id}")
        return context

