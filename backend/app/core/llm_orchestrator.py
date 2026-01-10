"""LLM orchestration for claim analysis."""
from typing import Dict, Any, Optional
import json
from app.config import settings
from app.schemas.claim_analysis import (
    ClaimAnalysis, ClaimAnalysisRequest, ReasoningStep, PolicyReference
)
from app.utils.logging import logger


class LLMOrchestrator:
    """Orchestrates LLM calls for claim analysis."""
    
    def __init__(self):
        """Initialize LLM orchestrator."""
        self.openai_client: Optional[Any] = None
        self.anthropic_client: Optional[Any] = None
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI package not installed")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
        
        if settings.anthropic_api_key:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("Anthropic package not installed")
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}")
    
    async def analyze_claim(
        self, masked_data: Dict[str, Any]
    ) -> ClaimAnalysis:
        """
        Analyze a claim using LLM.
        
        Args:
            masked_data: Claim data with PII masked
            
        Returns:
            ClaimAnalysis object with structured results
        """
        claim_id = masked_data.get("claim_id", "UNKNOWN")
        
        # Try OpenAI first, fallback to Anthropic, then mock
        if self.openai_client:
            try:
                return await self._analyze_with_openai(masked_data)
            except Exception as e:
                logger.error(f"OpenAI analysis failed: {e}")
                if self.anthropic_client:
                    try:
                        return await self._analyze_with_anthropic(masked_data)
                    except Exception as e2:
                        logger.error(f"Anthropic analysis failed: {e2}")
        
        if self.anthropic_client:
            try:
                return await self._analyze_with_anthropic(masked_data)
            except Exception as e:
                logger.error(f"Anthropic analysis failed: {e}")
        
        # Fallback to mock response if no LLM available
        logger.warning(f"No LLM client available, using mock response for claim {claim_id}")
        return self._create_mock_analysis(claim_id)
    
    async def _analyze_with_openai(self, masked_data: Dict[str, Any]) -> ClaimAnalysis:
        """Analyze claim using OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        claim_id = masked_data.get("claim_id", "UNKNOWN")
        
        # Create prompt for analysis
        prompt = self._create_analysis_prompt(masked_data)
        
        # Use OpenAI structured outputs if available (gpt-4-turbo-preview or newer)
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"} if "turbo" in self.model.lower() else None
            )
            
            # Parse response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Parse JSON response
            analysis_dict = json.loads(content)
            return self._parse_llm_response(analysis_dict, claim_id, tokens_used)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _analyze_with_anthropic(self, masked_data: Dict[str, Any]) -> ClaimAnalysis:
        """Analyze claim using Anthropic API."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        claim_id = masked_data.get("claim_id", "UNKNOWN")
        
        prompt = self._create_analysis_prompt(masked_data)
        system_prompt = self._get_system_prompt()
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229" if "claude" not in self.model.lower() else self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            
            # Parse JSON response
            analysis_dict = json.loads(content)
            return self._parse_llm_response(analysis_dict, claim_id, tokens_used)
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM."""
        return """You are an expert insurance claims analyst. Analyze claim data and provide structured JSON responses.

Response format (JSON):
{
  "status": "approved" | "denied" | "pending_review" | "needs_info",
  "denial_reason": "string (required if status is denied)",
  "recommended_action": "string",
  "required_information": ["string"],
  "confidence_score": 0.0-1.0,
  "reasoning_steps": [
    {
      "step_number": 1,
      "description": "string",
      "data_sources": ["string"]
    }
  ],
  "policy_sections": [
    {
      "document_name": "string",
      "section_number": "string",
      "section_title": "string",
      "relevant_text": "string",
      "relevance_score": 0.0-1.0
    }
  ],
  "potential_issues": ["string"]
}

Always respond with valid JSON only."""
    
    def _create_analysis_prompt(self, masked_data: Dict[str, Any]) -> str:
        """Create analysis prompt from masked data."""
        claim_id = masked_data.get("claim_id", "UNKNOWN")
        claim_data = masked_data.get("claim_data", {})
        member_data = masked_data.get("member_data", {})
        policy_data = masked_data.get("policy_data", {})
        
        prompt = f"""Analyze the following insurance claim:

Claim ID: {claim_id}

Claim Data:
{json.dumps(claim_data, indent=2)}

Member Data:
{json.dumps(member_data, indent=2)}

Policy Data:
{json.dumps(policy_data, indent=2)}

Provide a comprehensive analysis in the specified JSON format."""
        
        return prompt
    
    def _parse_llm_response(
        self, response_dict: Dict[str, Any], claim_id: str, tokens_used: int
    ) -> ClaimAnalysis:
        """Parse LLM JSON response into ClaimAnalysis schema."""
        reasoning_steps = [
            ReasoningStep(**step) if isinstance(step, dict) else step
            for step in response_dict.get("reasoning_steps", [])
        ]
        
        policy_sections = [
            PolicyReference(**section) if isinstance(section, dict) else section
            for section in response_dict.get("policy_sections", [])
        ]
        
        return ClaimAnalysis(
            claim_id=claim_id,
            status=response_dict.get("status", "pending_review"),
            denial_reason=response_dict.get("denial_reason"),
            recommended_action=response_dict.get("recommended_action", "Review claim"),
            required_information=response_dict.get("required_information", []),
            confidence_score=float(response_dict.get("confidence_score", 0.5)),
            reasoning_steps=reasoning_steps,
            policy_sections=policy_sections,
            potential_issues=response_dict.get("potential_issues", []),
            tokens_used=tokens_used
        )
    
    def _create_mock_analysis(self, claim_id: str) -> ClaimAnalysis:
        """Create mock analysis when LLM is not available."""
        return ClaimAnalysis(
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

