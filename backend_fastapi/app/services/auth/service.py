"""Authentication service - application layer."""
from datetime import timedelta
from loguru import logger
from opentelemetry import trace
from fastapi import HTTPException, status

from app.core.database.interfaces import IUserManager
from app.schemas.user.models import User
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.core.config import settings

tracer = trace.get_tracer(__name__)


class AuthService:
    """Service layer for handling authentication business logic."""
    
    def __init__(self, user_manager: IUserManager):
        """Initialize with user manager via dependency injection."""
        self.user_manager = user_manager
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate user and return JWT token with permissions.
        
        Args:
            email: User's email address
            password: User's plain text password
            
        Returns:
            Dictionary with access_token and token_type
            
        Raises:
            HTTPException: If authentication fails
        """
        with tracer.start_as_current_span("auth_service_authenticate") as span:
            span.set_attribute("user.email", email)
            logger.info(f"Login attempt for email: {email}")
            
            # Find user by email
            user = await self.user_manager.find_by_email(email)
            if not user:
                logger.warning(f"Login failed: User not found for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Login failed: Invalid password for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Create JWT token with permissions
            access_token_expires = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
            access_token = create_access_token(
                data={
                    "sub": user.id,
                    "email": user.email,
                    "permissions": user.permissions or []
                },
                expires_delta=access_token_expires
            )
            
            span.set_attribute("user.id", user.id)
            logger.info(f"Login successful for user: {user.id}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }

