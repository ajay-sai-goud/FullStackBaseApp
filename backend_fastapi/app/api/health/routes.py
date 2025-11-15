"""Health check API endpoints."""
from fastapi import APIRouter, status, Depends
from loguru import logger

from app.schemas.health import HealthStatus
from app.services.health import HealthService
from app.core.observability import TracingAPIRoute
from app.core.dependencies import get_health_service

router = APIRouter(route_class=TracingAPIRoute, prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
)
async def health_check(
    health_service: HealthService = Depends(get_health_service)
) -> HealthStatus:
    """
    Endpoint to check the health of the application.
    It delegates the actual health check logic to the HealthService.
    """
    logger.info("Health check endpoint was called.")
    return await health_service.get_health_status()

