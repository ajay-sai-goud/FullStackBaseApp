"""ID generation utilities for domain entities."""
from uuid import uuid4


def generate_user_id() -> str:
    """Generate a unique user ID with prefix."""
    return f"user_{uuid4().hex}"


def generate_file_id() -> str:
    """Generate a unique file ID with prefix."""
    return f"file_{uuid4().hex}"


def generate_id(prefix: str) -> str:
    """Generate a generic ID with custom prefix."""
    return f"{prefix}_{uuid4().hex}"

