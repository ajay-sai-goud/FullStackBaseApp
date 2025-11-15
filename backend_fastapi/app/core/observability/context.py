"""Context variables for request-scoped data."""
from contextvars import ContextVar

# Context variable for storing client IP address
client_ip_context: ContextVar[str | None] = ContextVar("client_ip", default=None)

