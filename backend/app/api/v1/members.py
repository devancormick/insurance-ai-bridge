"""Members API endpoints."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.core.cache import cache
from app.core.exceptions import MemberNotFoundError
from app.core.data_aggregator import DataAggregator
from app.utils.logging import logger

router = APIRouter()


@router.get("/{member_id}", summary="Get member information")
async def get_member(member_id: str) -> dict:
    """
    Get member information by ID.
    
    Args:
        member_id: Unique member identifier
        
    Returns:
        Member information dictionary
        
    Raises:
        MemberNotFoundError: If member not found
    """
    # Check cache first
    cache_key = f"member:{member_id}"
    cached = await cache.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for member {member_id}")
        return cached
    
    # Fetch from data aggregator
    data_aggregator = DataAggregator()
    
    try:
        member_data = await data_aggregator.db_client.get_member_data(member_id)
        
        if not member_data:
            raise MemberNotFoundError(member_id)
        
        # Cache for 10 minutes (member data changes less frequently)
        await cache.set(cache_key, member_data, ttl=600)
        
        return member_data
        
    except MemberNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching member {member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching member: {str(e)}"
        )


@router.get("/{member_id}/claims", summary="Get member claims history")
async def get_member_claims(
    member_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
) -> dict:
    """
    Get claim history for a member.
    
    Args:
        member_id: Unique member identifier
        limit: Maximum number of claims to return
        offset: Number of claims to skip
        
    Returns:
        Dictionary with claims list and pagination metadata
    """
    # Check cache
    cache_key = f"member:{member_id}:claims:limit:{limit}:offset:{offset}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    data_aggregator = DataAggregator()
    
    try:
        # TODO: Implement actual query for member claims
        # For now, return empty list
        claims = []
        
        result = {
            "member_id": member_id,
            "claims": claims,
            "total": len(claims),
            "limit": limit,
            "offset": offset
        }
        
        # Cache for 5 minutes
        await cache.set(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching member claims for {member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching member claims: {str(e)}"
        )

