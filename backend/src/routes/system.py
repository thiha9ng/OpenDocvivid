"""
Translation routes module for AI DocVivid Service
"""

from fastapi import APIRouter, Depends
from src.utils.logger import get_logger
from src.configs.config import settings
# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()

# Health check
@router.get("/health")
async def health_check():
    """Health check API"""
    logger.info("Executing health check...")
    return {"status": "ok", "data": {"environment": settings.environment}} 