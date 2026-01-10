"""Tests for LLM orchestrator."""
import pytest
from app.core.llm_orchestrator import LLMOrchestrator


@pytest.mark.asyncio
async def test_llm_orchestrator_initialization():
    """Test LLM orchestrator initialization."""
    orchestrator = LLMOrchestrator()
    
    # Should initialize without errors even if no API keys
    assert orchestrator is not None


@pytest.mark.asyncio
async def test_analyze_claim_with_mock():
    """Test claim analysis with mock response."""
    orchestrator = LLMOrchestrator()
    
    masked_data = {
        "claim_id": "CLM-TEST-123",
        "claim_data": {
            "amount": 5000.00,
            "type": "medical"
        },
        "member_data": {},
        "policy_data": {}
    }
    
    result = await orchestrator.analyze_claim(masked_data)
    
    assert result.claim_id == "CLM-TEST-123"
    assert result.status in ["approved", "denied", "pending_review", "needs_info"]
    assert result.confidence_score >= 0.0 and result.confidence_score <= 1.0
    assert len(result.reasoning_steps) > 0
    assert result.tokens_used >= 0


@pytest.mark.asyncio
async def test_mock_analysis_structure():
    """Test that mock analysis has correct structure."""
    orchestrator = LLMOrchestrator()
    result = orchestrator._create_mock_analysis("TEST-123")
    
    assert result.claim_id == "TEST-123"
    assert result.status == "pending_review"
    assert result.recommended_action is not None
    assert result.confidence_score == 0.85
    assert len(result.reasoning_steps) == 1
    assert result.policy_sections == []
    assert result.potential_issues == []

