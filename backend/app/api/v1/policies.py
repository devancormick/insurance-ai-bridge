"""Policies API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.cache import cache
from app.core.exceptions import PolicyNotFoundError
from app.utils.logging import logger
from app.core.data_aggregator import DataAggregator

router = APIRouter()


@router.get("/{policy_id}", summary="Get policy information")
async def get_policy(
    policy_id: str,
    include_documents: bool = False
) -> dict:
    """
    Get policy information by ID.
    
    Args:
        policy_id: Unique policy identifier
        include_documents: Include policy documents from SharePoint
        
    Returns:
        Policy information dictionary
        
    Raises:
        PolicyNotFoundError: If policy not found
    """
    # Check cache first
    cache_key = f"policy:{policy_id}:docs:{include_documents}"
    cached = await cache.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for policy {policy_id}")
        return cached
    
    # Fetch from data aggregator
    data_aggregator = DataAggregator()
    
    try:
        policy_data = await data_aggregator.db_client.get_policy_data(policy_id)
        
        if not policy_data:
            raise PolicyNotFoundError(policy_id)
        
        if include_documents:
            documents = await data_aggregator.sharepoint_client.get_policy_documents(policy_id)
            policy_data["documents"] = documents
        
        # Cache for 5 minutes
        await cache.set(cache_key, policy_data, ttl=300)
        
        return policy_data
        
    except PolicyNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching policy {policy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policy: {str(e)}"
        )


@router.get("/{policy_id}/members", summary="Get policy members")
async def get_policy_members(policy_id: str) -> List[dict]:
    """
    Get all members associated with a policy.
    
    Args:
        policy_id: Unique policy identifier
        
    Returns:
        List of member dictionaries
    """
    data_aggregator = DataAggregator()
    
    try:
        policy_data = await data_aggregator.db_client.get_policy_data(policy_id)
        if not policy_data:
            raise PolicyNotFoundError(policy_id)
        
        member_id = policy_data.get("member_id")
        if not member_id:
            return []
        
        member_data = await data_aggregator.db_client.get_member_data(member_id)
        return [member_data] if member_data else []
        
    except PolicyNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching policy members for {policy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching policy members: {str(e)}"
        )

