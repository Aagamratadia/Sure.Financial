"""Health check endpoint"""
from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow(),
        services={
            "pdf_parser": "operational",
            "ocr_engine": "operational",
            "database": "operational"
        }
    )
