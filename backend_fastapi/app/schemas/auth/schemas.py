"""Authentication request/response schemas."""
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.utils.validators import validate_email_format, validate_password_strength


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password (min 6 chars, must contain: 1 uppercase, 1 lowercase, 1 number, 1 special char @$!%*?&#)")
    
    # Use centralized validators
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email using centralized validator."""
        if not isinstance(v, str):
            raise ValueError("Email must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Email cannot be empty or whitespace only")
        return validate_email_format(v)
    
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


class TokenResponse(BaseModel):
    """Response schema for JWT token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")

