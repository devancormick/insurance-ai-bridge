"""API v1 router."""
from fastapi import APIRouter
from app.api.v1 import claims

api_router = APIRouter()

# Include route modules
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])

# TODO: Add other routers when implemented
# from app.api.v1 import policies, members
# api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
# api_router.include_router(members.router, prefix="/members", tags=["members"])

