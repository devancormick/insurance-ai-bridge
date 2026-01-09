"""Pydantic schemas for claim analysis."""
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List
from datetime import datetime


class ClaimAnalysisRequest(BaseModel):
    """Request schema for claim analysis."""
    claim_id: str = Field(..., description="Unique claim identifier")
    include_member_history: bool = Field(default=True)
    include_policy_docs: bool = Field(default=True)


class PolicyReference(BaseModel):
    """Reference to a specific policy section."""
    document_name: str = Field(..., max_length=200)
    section_number: str = Field(..., max_length=50)
    section_title: str = Field(..., max_length=200)
    relevant_text: str = Field(..., max_length=1000)
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class ReasoningStep(BaseModel):
    """Single step in the AI's reasoning process."""
    step_number: int = Field(..., ge=1)
    description: str = Field(..., max_length=500)
    data_sources: List[str]


class ClaimAnalysis(BaseModel):
    """Structured output from LLM claim analysis."""
    claim_id: str
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core decision
    status: Literal["approved", "denied", "pending_review", "needs_info"]
    
    # Required when status is denied
    denial_reason: Optional[str] = Field(None, max_length=500)
    
    # Policy references
    policy_sections: List[PolicyReference] = Field(default_factory=list)
    
    # Recommended action
    recommended_action: str = Field(..., max_length=500)
    
    # Additional information needed
    required_information: Optional[List[str]] = None
    
    # Confidence and reasoning
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning_steps: List[ReasoningStep] = Field(..., min_length=1)
    
    # Risk flags
    potential_issues: List[str] = Field(default_factory=list)
    
    # Token usage
    tokens_used: int = Field(..., ge=0)
    
    @field_validator('denial_reason')
    @classmethod
    def denial_reason_required_when_denied(cls, v, info):
        """Validate that denial_reason is provided when status is denied."""
        if info.data.get('status') == 'denied' and not v:
            raise ValueError('denial_reason required when status is denied')
        return v


class ClaimAnalysisResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[ClaimAnalysis] = None
    error: Optional[str] = None
    processing_time_ms: int

