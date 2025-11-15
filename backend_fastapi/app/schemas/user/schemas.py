"""User domain Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from app.utils.validators import (
    validate_password_strength,
    validate_email_format,
    validate_permissions,
    validate_user_id,
)

class UserBase(BaseModel):
    """Base model for a user, containing common fields."""
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    email: EmailStr = Field(..., description="User's email address (unique)")
    
    # Use centralized email validator
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email using centralized validator."""
        return validate_email_format(v)

class UserCreate(UserBase):
    """Model for creating a new user. Inherits from UserBase."""
    password: str = Field(
        ..., 
        description="User password (min 6 chars, must contain: 1 uppercase, 1 lowercase, 1 number, 1 special char @$!%*?&#)"
    )
    confirm_password: str = Field(
        ...,
        description="Password confirmation (must match password)"
    )
    permissions: Optional[List[str]] = Field(
        default=None,
        description="User permissions list. If not provided, defaults to ['read:audio', 'write:audio']"
    )
    
    # Use centralized validators
    @field_validator('first_name', mode='before')
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate and trim first name."""
        if not isinstance(v, str):
            raise ValueError("First name must be a string")
        v = v.strip()
        if not v:
            raise ValueError("First name cannot be empty or whitespace only")
        if len(v) > 100:
            raise ValueError("First name cannot exceed 100 characters")
        return v
    
    @field_validator('last_name', mode='before')
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate and trim last name."""
        if not isinstance(v, str):
            raise ValueError("Last name must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Last name cannot be empty or whitespace only")
        if len(v) > 100:
            raise ValueError("Last name cannot exceed 100 characters")
        return v
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password using centralized validator."""
        if not isinstance(v, str):
            raise ValueError("Password must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Password cannot be empty or whitespace only")
        return validate_password_strength(v)
    
    @field_validator('confirm_password', mode='before')
    @classmethod
    def validate_confirm_password(cls, v: str) -> str:
        """Validate confirm_password format (same as password)."""
        if not isinstance(v, str):
            raise ValueError("Confirm password must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Confirm password cannot be empty or whitespace only")
        # Only validate format, not match (that's done in model_validator)
        return validate_password_strength(v)
    
    @field_validator('permissions', mode='before')
    @classmethod
    def validate_permissions(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate permissions using centralized validator."""
        return validate_permissions(v)
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validate that password and confirm_password match."""
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm_password do not match")
        return self

class UserUpdate(BaseModel):
    """Model for updating a user. All fields are optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's last name")
    email: Optional[EmailStr] = Field(None, description="User's email address (unique)")
    password: Optional[str] = Field(
        None, 
        description="User password (min 6 chars, must contain: 1 uppercase, 1 lowercase, 1 number, 1 special char @$!%*?&#)"
    )
    permissions: Optional[List[str]] = Field(None, description="User permissions list")
    
    # Use centralized validators (only validate if value is provided)
    @field_validator('first_name', mode='before')
    @classmethod
    def validate_first_name_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Validate first name only if provided. Reject empty strings."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("First name cannot be empty or whitespace only")
            if len(v) < 1:
                raise ValueError("First name must be at least 1 character")
            if len(v) > 100:
                raise ValueError("First name cannot exceed 100 characters")
        return v
    
    @field_validator('last_name', mode='before')
    @classmethod
    def validate_last_name_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Validate last name only if provided. Reject empty strings."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Last name cannot be empty or whitespace only")
            if len(v) < 1:
                raise ValueError("Last name must be at least 1 character")
            if len(v) > 100:
                raise ValueError("Last name cannot exceed 100 characters")
        return v
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Validate password only if provided. Reject empty strings."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Password cannot be empty or whitespace only")
            return validate_password_strength(v)
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Validate email only if provided. Reject empty strings."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Email cannot be empty or whitespace only")
            return validate_email_format(v)
    
    @field_validator('permissions', mode='before')
    @classmethod
    def validate_permissions_if_provided(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate permissions only if provided."""
        if v is not None:
            return validate_permissions(v)
        return v

class UserDisplay(UserBase):
    """Model for displaying user information in API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="The unique identifier for the user.")
    permissions: List[str] = Field(..., description="User permissions list")
    created_at: datetime = Field(..., description="The timestamp of when the user was created.")
    updated_at: datetime = Field(..., description="The timestamp of when the user was last updated.")

class UserListQueryParams(BaseModel):
    """Query parameters for listing users."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of records to return")


class UserIdPathParams(BaseModel):
    """Path parameters for user ID."""
    user_id: str = Field(..., min_length=1, description="User unique identifier")
    
    # Use centralized user ID validator
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID using centralized validator."""
        if v is None:
            raise ValueError("User ID is required and cannot be null")
        if not isinstance(v, str):
            raise ValueError("User ID must be a string")
        v = v.strip()
        if not v:
            raise ValueError("User ID cannot be empty or whitespace only")
        return validate_user_id(v, strict=False)


class PermissionsResponse(BaseModel):
    """Response model for permissions list."""
    permissions: List[str] = Field(..., description="List of all available permissions in the system")

