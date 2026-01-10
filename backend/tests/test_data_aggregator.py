"""Tests for data aggregator."""
import pytest
from app.core.data_aggregator import DataAggregator


@pytest.mark.asyncio
async def test_data_aggregator_initialization():
    """Test data aggregator initialization."""
    aggregator = DataAggregator()
    
    assert aggregator is not None
    # Clients may be None if not configured, which is fine
    assert hasattr(aggregator, 'db_client')
    assert hasattr(aggregator, 'soap_client')
    assert hasattr(aggregator, 'sharepoint_client')


@pytest.mark.asyncio
async def test_get_claim_context():
    """Test claim context aggregation."""
    aggregator = DataAggregator()
    
    context = await aggregator.get_claim_context(
        claim_id="CLM-TEST-123",
        include_history=True,
        include_docs=True
    )
    
    assert context is not None
    assert context["claim_id"] == "CLM-TEST-123"
    assert "claim_data" in context
    assert "member_data" in context
    assert "policy_data" in context
    assert "documents" in context
    assert isinstance(context["documents"], list)


@pytest.mark.asyncio
async def test_get_claim_context_without_history():
    """Test claim context without history."""
    aggregator = DataAggregator()
    
    context = await aggregator.get_claim_context(
        claim_id="CLM-TEST-123",
        include_history=False,
        include_docs=False
    )
    
    assert context["claim_id"] == "CLM-TEST-123"
    # Should still have structure even without history/docs
    assert "documents" in context

