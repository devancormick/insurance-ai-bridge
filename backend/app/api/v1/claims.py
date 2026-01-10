"""Claims API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.claim_analysis import ClaimAnalysisRequest, ClaimAnalysisResponse
from app.core.pii_handler import PIIHandler
from app.core.data_aggregator import DataAggregator
from app.core.llm_orchestrator import LLMOrchestrator
from app.utils.logging import logger
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
        
        # Call LLM orchestrator for analysis
        analysis = await llm_orchestrator.analyze_claim(masked_context)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ClaimAnalysisResponse(
            success=True,
            data=analysis,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error analyzing claim {claim_id}: {e}", exc_info=True)
        processing_time_ms = int((time.time() - start_time) * 1000)
        return ClaimAnalysisResponse(
            success=False,
            error=str(e),
            processing_time_ms=processing_time_ms
        )
    finally:
        # Clear PII tokens (zero retention)
        if 'pii_handler' in locals():
            pii_handler.clear_tokens()

