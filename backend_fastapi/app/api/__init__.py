"""This package contains the API routing layer."""
from fastapi import APIRouter

from app.core.observability import TracingAPIRoute
from app.api.health import health_router
from app.api.user import user_router
from app.api.ui import ui_router
from app.api.auth import router as auth_router
from app.api.audio import router as audio_router

# Main API router that combines all domain routers
api_router = APIRouter(route_class=TracingAPIRoute)

# Include all domain routers
api_router.include_router(health_router)
api_router.include_router(user_router)
api_router.include_router(audio_router)
api_router.include_router(auth_router)

__all__ = ["api_router", "ui_router"]
