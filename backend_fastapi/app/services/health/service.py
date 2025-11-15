"""Health domain service - application layer."""
from loguru import logger
from opentelemetry import trace

from app.schemas.health import HealthStatus

tracer = trace.get_tracer(__name__)

class HealthService:
    """
    Service layer for handling health-related business logic.
    """

    @staticmethod
    async def get_health_status() -> HealthStatus:
        """
        Checks the application's health and returns its status.

        This is where you would add checks for database connections,
        external service availability, etc.
        """
        with tracer.start_as_current_span("health_service_check") as span:
            logger.info("Performing health check in service layer.")
            # For now, we return a simple "ok" status.
            health = HealthStatus(status="ok")
            span.set_attribute("service.health.status", health.status)
            return health

