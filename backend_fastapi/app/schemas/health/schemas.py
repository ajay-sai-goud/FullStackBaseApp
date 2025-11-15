"""Health domain Pydantic schemas."""
from pydantic import BaseModel, Field

class HealthStatus(BaseModel):
    """
    Pydantic model for the health check endpoint response.
    """
    status: str = Field(..., description="The operational status of the service.", example="ok")

