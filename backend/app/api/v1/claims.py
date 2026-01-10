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


@router.post(
    "/{claim_id}/analyze",
    response_model=ClaimAnalysisResponse,
    summary="Analyze a claim using AI",
    description="""
    Analyze an insurance claim using AI/LLM processing.
    
    This endpoint:
    1. Aggregates claim data from multiple sources (legacy DB, SOAP API, SharePoint)
    2. Masks PII (names, SSNs, DOBs) before sending to LLM
    3. Sends masked data to LLM for analysis
    4. Returns structured analysis with reasoning and policy references
    
    **PII Handling**: All PII is tokenized before LLM processing and tokens are cleared after (zero retention).
    
    **Rate Limit**: 50 requests per minute per IP
    """,
    responses={
        200: {
            "description": "Analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "claim_id": "CLM-12345",
                            "status": "approved",
                            "confidence_score": 0.95,
                            "recommended_action": "Approve claim",
                            "tokens_used": 1250
                        },
                        "processing_time_ms": 1234
                    }
                }
            }
        },
        404: {"description": "Claim not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    },
    tags=["claims"]
)
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

