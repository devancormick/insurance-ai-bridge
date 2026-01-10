"""Claims API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.claim_analysis import ClaimAnalysisRequest, ClaimAnalysisResponse
from app.core.pii_handler import PIIHandler
from app.core.data_aggregator import DataAggregator
from app.core.llm_orchestrator import LLMOrchestrator
import time

router = APIRouter()


@router.post("/{claim_id}/analyze", response_model=ClaimAnalysisResponse)
async def analyze_claim(claim_id: str, request: ClaimAnalysisRequest) -> ClaimAnalysisResponse:
    """
    Analyze a claim using AI.
    
    This endpoint aggregates claim data, masks PII, sends to LLM,
    and returns structured analysis.
    """
    start_time = time.time()
    
    try:
        # Initialize handlers
        pii_handler = PIIHandler()
        data_aggregator = DataAggregator()
        llm_orchestrator = LLMOrchestrator()
        
        # Aggregate data from multiple sources
        context = await data_aggregator.get_claim_context(
            claim_id=claim_id,
            include_history=request.include_member_history,
            include_docs=request.include_policy_docs
        )
        
        # Mask PII before sending to LLM
        masked_context = pii_handler.mask_pii(context)
        
        # TODO: Call LLM orchestrator (currently not implemented)
        # For now, return a mock response
        from app.schemas.claim_analysis import ClaimAnalysis, ReasoningStep, PolicyReference
        
        mock_analysis = ClaimAnalysis(
            claim_id=claim_id,
            status="pending_review",
            recommended_action="Review claim documentation for completeness",
            confidence_score=0.85,
            reasoning_steps=[
                ReasoningStep(
                    step_number=1,
                    description="Claim data aggregated from multiple sources",
                    data_sources=["legacy_db", "soap_api"]
                )
            ],
            policy_sections=[],
            potential_issues=[],
            tokens_used=0
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ClaimAnalysisResponse(
            success=True,
            data=mock_analysis,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        return ClaimAnalysisResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time_ms
        )
    finally:
        # Clear PII tokens (zero retention)
        pii_handler.clear_tokens()

