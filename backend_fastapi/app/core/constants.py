"""Application constants for permissions, roles, and validation."""

# Validation constants
class ValidationConstants:
    """Constants for input validation."""
    
    # Password validation
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 128
    
    # Email validation (RFC 5321 limits)
    MAX_EMAIL_LENGTH = 254
    MAX_EMAIL_LOCAL_PART_LENGTH = 64


# Permission constants
class Permissions:
    """Permission constants for RBAC."""
    
    # Audio permissions
    READ_AUDIO = "read:audio"
    WRITE_AUDIO = "write:audio"
    DELETE_AUDIO = "delete:audio"
    
    # User permissions
    READ_USER = "read:user"
    WRITE_USER = "write:user"
    DELETE_USER = "delete:user"
    
    # Admin permissions
    ADMIN = "admin"
    
    # All permissions list
    ALL_PERMISSIONS = [
        READ_AUDIO,
        WRITE_AUDIO,
        DELETE_AUDIO,
        READ_USER,
        WRITE_USER,
        DELETE_USER,
        ADMIN,
    ]


# Default permissions for new users
DEFAULT_USER_PERMISSIONS = [
    Permissions.READ_AUDIO,
    Permissions.WRITE_AUDIO,
]

# Role-based permission mappings
ROLE_PERMISSIONS = {
    "viewer": [
        Permissions.READ_AUDIO,
    ],
    "user": [
        Permissions.READ_AUDIO,
        Permissions.WRITE_AUDIO,
    ],
    "admin": [
        Permissions.READ_AUDIO,
        Permissions.WRITE_AUDIO,
        Permissions.DELETE_AUDIO,
        Permissions.READ_USER,
        Permissions.WRITE_USER,
        Permissions.DELETE_USER,
        Permissions.ADMIN,
    ],
}

