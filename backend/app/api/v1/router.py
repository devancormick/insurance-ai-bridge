"""API v1 router."""
from fastapi import APIRouter
from app.api.v1 import claims, auth, policies, members, metrics, search

api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["monitoring"])

