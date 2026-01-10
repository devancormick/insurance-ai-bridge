"""API documentation enhancements."""
from typing import Dict, Any
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi

router = APIRouter()


def custom_openapi_schema() -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced documentation.
    
    Returns:
        OpenAPI schema dictionary
    """
    from app.main import app
    from app.config import settings
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        Insurance AI Bridge API - AI-powered claim analysis system.
        
        ## Features
        
        - **Claim Analysis**: Analyze insurance claims using AI/LLM
        - **PII Protection**: Zero-retention PII handling with tokenization
        - **Data Aggregation**: Multi-source data integration
        - **Authentication**: JWT-based authentication
        
        ## Authentication
        
        Most endpoints require authentication. Get a token by:
        
        1. POST `/api/v1/auth/login` with username and password
        2. Include the token in Authorization header: `Bearer <token>`
        
        ## Rate Limiting
        
        - Auth endpoints: 5 requests/minute
        - API endpoints: 50-100 requests/minute
        - Rate limit headers are included in all responses
        
        ## PII Handling
        
        All PII is masked before sending to LLM. Tokens are cleared after processing (zero retention).
        """,
        routes=app.routes,
    )
    
    # Add custom documentation
    openapi_schema["info"]["contact"] = {
        "name": "Insurance AI Bridge Support"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "Proprietary",
        "url": "https://example.com/license"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": settings.api_url,
            "description": "Production server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token from /api/v1/auth/login"
        }
    }
    
    # Add examples to schemas
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
        
        # Add example to ClaimAnalysisRequest
        if "ClaimAnalysisRequest" in schemas:
            schemas["ClaimAnalysisRequest"]["example"] = {
                "claim_id": "CLM-12345",
                "include_member_history": True,
                "include_policy_docs": True
            }
        
        # Add example to ClaimAnalysis
        if "ClaimAnalysis" in schemas:
            schemas["ClaimAnalysis"]["example"] = {
                "claim_id": "CLM-12345",
                "status": "approved",
                "confidence_score": 0.95,
                "recommended_action": "Approve claim based on policy coverage",
                "reasoning_steps": [
                    {
                        "step_number": 1,
                        "description": "Verified claim details match policy coverage",
                        "data_sources": ["legacy_db", "soap_api"]
                    }
                ],
                "policy_sections": [],
                "potential_issues": [],
                "tokens_used": 1250
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

