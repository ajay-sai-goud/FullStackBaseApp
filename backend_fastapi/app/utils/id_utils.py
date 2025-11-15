"""ID generation utilities for domain entities."""
from uuid import uuid4, uuid5, NAMESPACE_DNS


# Fixed namespace UUID for deterministic ID generation
# This ensures the same email always generates the same user ID
APP_NAMESPACE_UUID = uuid5(NAMESPACE_DNS, "app.user.id")


def generate_user_id() -> str:
    """Generate a unique user ID with prefix."""
    return f"user_{uuid4().hex}"


def generate_deterministic_user_id(email: str) -> str:
    """Generate a deterministic user ID based on email.
    
    Uses UUID5 to ensure the same email always produces the same ID.
    This prevents duplicate users when multiple workers try to create
    the same user (e.g., default admin) simultaneously.
    
    Args:
        email: User email address
        
    Returns:
        Deterministic user ID with prefix
    """
    deterministic_uuid = uuid5(APP_NAMESPACE_UUID, email.lower().strip())
    return f"user_{deterministic_uuid.hex}"


def generate_file_id() -> str:
    """Generate a unique file ID with prefix."""
    return f"file_{uuid4().hex}"


def generate_id(prefix: str) -> str:
    """Generate a generic ID with custom prefix."""
    return f"{prefix}_{uuid4().hex}"

