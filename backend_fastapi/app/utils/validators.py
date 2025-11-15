"""Centralized validation utilities for use across the application."""
import re
from typing import Optional, List

from app.core.constants import Permissions, ValidationConstants

# Password validation patterns
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{6,}$'
)
# Alternative simpler pattern (at least 6 chars, can be more lenient)
SIMPLE_PASSWORD_PATTERN = re.compile(r'.{6,}')

# Email validation pattern (EmailStr already handles this, but for custom validation)
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_password_strength(password: str) -> str:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 6 characters
    - Maximum 128 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character (@$!%*?&#)
    
    Args:
        password: Password string to validate
        
    Returns:
        Validated password string
        
    Raises:
        ValueError: If password doesn't meet requirements
    """
    if not password:
        raise ValueError("Password is required")
    
    if len(password) < ValidationConstants.MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {ValidationConstants.MIN_PASSWORD_LENGTH} characters long"
        )
    
    if len(password) > ValidationConstants.MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at most {ValidationConstants.MAX_PASSWORD_LENGTH} characters long"
        )
    
    # Check for required character types
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '@$!%*?&#' for c in password)
    
    errors = []
    if not has_uppercase:
        errors.append("one uppercase letter")
    if not has_lowercase:
        errors.append("one lowercase letter")
    if not has_digit:
        errors.append("one number")
    if not has_special:
        errors.append("one special character (@$!%*?&#)")
    
    if errors:
        error_msg = "Password must contain at least " + ", ".join(errors)
        raise ValueError(error_msg)
    
    return password


def validate_email_format(email: str) -> str:
    """
    Validate email format.
    
    Note: Pydantic's EmailStr already validates email format,
    but this can be used for additional custom validation.
    
    Args:
        email: Email string to validate
        
    Returns:
        Validated email string
        
    Raises:
        ValueError: If email format is invalid
    """
    if not email:
        raise ValueError("Email is required")
    
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    
    email = email.strip().lower()
    
    if not email:
        raise ValueError("Email cannot be empty or whitespace only")
    
    if not EMAIL_PATTERN.match(email):
        raise ValueError("Invalid email format")
    
    # Additional checks
    if len(email) > ValidationConstants.MAX_EMAIL_LENGTH:
        raise ValueError(
            f"Email address is too long (maximum {ValidationConstants.MAX_EMAIL_LENGTH} characters)"
        )
    
    local_part, domain = email.split('@', 1)
    if len(local_part) > ValidationConstants.MAX_EMAIL_LOCAL_PART_LENGTH:
        raise ValueError(
            f"Email local part is too long (maximum {ValidationConstants.MAX_EMAIL_LOCAL_PART_LENGTH} characters)"
        )
    
    return email


def validate_permissions(permissions: Optional[List[str]]) -> Optional[List[str]]:
    """
    Validate that all permissions in the list are valid.
    
    Args:
        permissions: List of permission strings to validate
        
    Returns:
        Validated permissions list
        
    Raises:
        ValueError: If any permission is invalid
    """
    if permissions is None:
        return permissions
    
    if not isinstance(permissions, list):
        raise ValueError("Permissions must be a list")
    
    if not permissions:  # Empty list is valid
        return permissions
    
    valid_permissions = set(Permissions.ALL_PERMISSIONS)
    invalid_permissions = [p for p in permissions if p not in valid_permissions]
    
    if invalid_permissions:
        valid_list = ", ".join(sorted(Permissions.ALL_PERMISSIONS))
        raise ValueError(
            f"Invalid permissions: {', '.join(invalid_permissions)}. "
            f"Valid permissions are: {valid_list}"
        )
    
    return permissions


def validate_user_id(user_id: str, strict: bool = False) -> str:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID string to validate
        strict: If True, validates that ID starts with "user_" prefix
        
    Returns:
        Validated user ID string
        
    Raises:
        ValueError: If user ID format is invalid
    """
    if not user_id:
        raise ValueError("User ID is required")
    
    if not isinstance(user_id, str):
        raise ValueError("User ID must be a string")
    
    user_id = user_id.strip()
    
    if len(user_id) < 1:
        raise ValueError("User ID cannot be empty")
    
    # Optional: Check if it starts with "user_" prefix (our ID format)
    # Only enforce if strict=True to allow flexibility
    if strict and not user_id.startswith("user_"):
        raise ValueError("Invalid user ID format. Must start with 'user_'")
    
    return user_id


def validate_file_id(file_id: str, strict: bool = False) -> str:
    """
    Validate file ID format.
    
    Args:
        file_id: File ID string to validate
        strict: If True, validates that ID starts with "file_" prefix
        
    Returns:
        Validated file ID string
        
    Raises:
        ValueError: If file ID format is invalid
    """
    if not file_id:
        raise ValueError("File ID is required")
    
    if not isinstance(file_id, str):
        raise ValueError("File ID must be a string")
    
    file_id = file_id.strip()
    
    if len(file_id) < 1:
        raise ValueError("File ID cannot be empty")
    
    # Optional: Check if it starts with "file_" prefix (our ID format)
    # Only enforce if strict=True to allow flexibility
    if strict and not file_id.startswith("file_"):
        raise ValueError("Invalid file ID format. Must start with 'file_'")
    
    return file_id


# Note: These functions are used directly in Pydantic schemas with @field_validator decorator.
# Example usage in schema:
#   @field_validator('password', mode='before')
#   @classmethod
#   def validate_password(cls, v: str) -> str:
#       return validate_password_strength(v)

