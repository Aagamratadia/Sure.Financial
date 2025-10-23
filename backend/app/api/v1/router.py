"""API v1 router"""
from fastapi import APIRouter
from app.api.v1.endpoints import parse, health
from app.api.endpoints import results

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(parse.router, prefix="/parse", tags=["Parsing"])
api_router.include_router(results.router, prefix="/results", tags=["Results"])
