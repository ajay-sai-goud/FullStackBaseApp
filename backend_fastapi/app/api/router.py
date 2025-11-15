"""Root API router configuration."""
from fastapi import APIRouter, FastAPI
from loguru import logger

from app.core import settings
from app.api import api_router, ui_router


def setup_routes(app: FastAPI):
    """
    Setup all API routes for the application.
    
    This function configures:
    - API routes with /api prefix (includes /api/audio, /api/users, /api/health, /api/login)
    - UI routes without prefix
    """
    # API routes with /api prefix (includes /api/audio, /api/users, /api/health, /api/login)
    app.include_router(api_router, prefix="/api")
    
    # UI routes without prefix (part of API layer per DDD)
    app.include_router(ui_router)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def read_root():
        """A welcome message for the root endpoint."""
        logger.info("Root endpoint was hit.")
        return {"message": f"Welcome to {settings.APP_NAME}"}

