"""FastAPI dependencies for dependency injection."""
from fastapi import Depends, Request, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.database.mongodb.user_manager import UserManager
from app.core.database.mongodb.file_manager import FileManager
from app.core.database.interfaces import IUserManager, IFileManager
from app.schemas.user.models import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.storage.interfaces import IStorageService
    from app.services.audio.interfaces import IAudioService
    from app.services.user.interfaces import IUserService
    from app.services.auth.interfaces import IAuthService
    from app.services.user import UserService
    from app.services.auth import AuthService
    from app.services.audio.service import AudioService
    from app.services.health import HealthService

# HTTP Bearer token security scheme with auto_error=False for flexible error handling
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None
) -> str:
    """
    Extract JWT token from request.
    
    Supports multiple formats:
    - Authorization: Bearer <token>
    - Authorization: <token>
    
    Raises HTTPException if no valid token found.
    """
    access_token: str | None = None
    
    # Try to get token from HTTPBearer credentials first
    if credentials:
        access_token = credentials.credentials
    else:
        # Fallback: Check Authorization header manually for raw token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 1:
                # Case: 'Authorization: <token>' (raw token without 'Bearer')
                access_token = parts[0]
            elif len(parts) == 2 and parts[0].lower() == "bearer":
                # Case: 'Authorization: Bearer <token>' (standard format)
                access_token = parts[1]
    
    # Raise error if no token found
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return access_token


def get_database(request: Request) -> AsyncIOMotorDatabase:
    """Get database instance from app state."""
    return request.app.state.db


def get_user_manager(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> IUserManager:
    """Get UserManager instance via dependency injection."""
    return UserManager(db)


def get_file_manager(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> IFileManager:
    """Get FileManager instance via dependency injection."""
    return FileManager(db)


def get_storage_service() -> "IStorageService":
    """Get StorageService instance via dependency injection."""
    from app.services.storage.storage_service import StorageService
    from app.core.config import settings
    
    return StorageService(
        bucket_name=settings.S3_BUCKET_NAME or "",
        region=settings.AWS_REGION,
        access_key_id=settings.AWS_ACCESS_KEY_ID or "",
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY or ""
    )


def get_auth_service(
    user_manager: IUserManager = Depends(get_user_manager)
) -> "IAuthService":
    """Get AuthService instance via dependency injection."""
    from app.services.auth import AuthService
    return AuthService(user_manager)


def get_audio_service(
    file_manager: IFileManager = Depends(get_file_manager),
    storage_service: "IStorageService" = Depends(get_storage_service)
) -> "IAudioService":
    """Get AudioService instance via dependency injection."""
    from app.services.audio.service import AudioService
    return AudioService(file_manager, storage_service)


def get_user_service(
    user_manager: IUserManager = Depends(get_user_manager),
    audio_service: "IAudioService" = Depends(get_audio_service)
) -> "IUserService":
    """Get UserService instance via dependency injection."""
    from app.services.user import UserService
    return UserService(user_manager, audio_service)


def get_health_service() -> "HealthService":
    """Get HealthService instance via dependency injection."""
    from app.services.health import HealthService
    return HealthService()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Stateless authentication - no database lookup required.
    JWT token signature validation is sufficient proof of authentication.
    
    Supports flexible token extraction:
    - Standard: Authorization: Bearer <token>
    - Raw token: Authorization: <token>
    
    Returns a minimal User object with id, email, and permissions from token.
    """
    # Extract token from request
    access_token = _extract_token(request, credentials)
    
    # Decode token and extract user information
    from app.utils.jwt import decode_token
    payload = decode_token(access_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create minimal User object from JWT token (no database lookup)
    # Only include fields that are actually used in routes (id, email, permissions)
    # Other fields are set to defaults since they're not accessed in routes
    from datetime import datetime
    return User(
        id=user_id,
        email=payload.get("email", ""),
        first_name="N/A",  # Not used in routes, placeholder value
        last_name="N/A",   # Not used in routes, placeholder value
        hashed_password="",  # Never expose password, placeholder value
        permissions=payload.get("permissions", []),
        created_at=datetime.utcnow(),  # Default timestamp (not used in routes)
        updated_at=datetime.utcnow()   # Default timestamp (not used in routes)
    )


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to require authentication. Returns authenticated user."""
    return current_user


def require_permissions(*required_permissions: str):
    """
    Decorator/dependency factory to require specific permissions.
    
    Optimized to use permissions from current_user instead of decoding token again.
    
    Usage:
        @router.get("/audio")
        async def list_audio(
            current_user: User = Depends(require_auth),
            permission: None = Depends(require_permissions("read:audio"))
        ):
            ...
    
    Or as a dependency:
        @router.delete("/audio/{id}")
        async def delete_audio(
            id: str,
            current_user: User = Depends(require_auth),
            permission: None = Depends(require_permissions("delete:audio"))
        ):
            ...
    """
    def permission_checker(
        current_user: User = Depends(require_auth)
    ) -> None:
        """Check if user has required permissions from current_user (no token re-decode)."""
        # Use permissions from current_user (already decoded in require_auth)
        # This avoids decoding the token twice!
        user_permissions = current_user.permissions or []
        
        # Admin permission grants all permissions
        if "admin" in user_permissions:
            logger.debug(f"Permission check passed (admin user). User has: {user_permissions}")
            return None
        
        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - set(user_permissions)
        
        if missing_permissions:
            logger.warning(
                f"Permission denied. Required: {required_permissions}, "
                f"User has: {user_permissions}, Missing: {missing_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {', '.join(missing_permissions)}"
            )
        
        logger.debug(f"Permission check passed. User has: {user_permissions}")
        return None
    
    return permission_checker


def require_any_permission(*required_permissions: str):
    """
    Decorator/dependency factory to require at least one of the specified permissions.
    
    Optimized to use permissions from current_user instead of decoding token again.
    
    Usage:
        @router.get("/audio")
        async def list_audio(
            current_user: User = Depends(require_auth),
            permission: None = Depends(require_any_permission("read:audio", "admin"))
        ):
            ...
    """
    def permission_checker(
        current_user: User = Depends(require_auth)
    ) -> None:
        """Check if user has at least one of the required permissions from current_user (no token re-decode)."""
        # Use permissions from current_user (already decoded in require_auth)
        # This avoids decoding the token twice!
        user_permissions = current_user.permissions or []
        
        # Admin permission grants all permissions
        if "admin" in user_permissions:
            logger.debug(f"Permission check passed (admin user). User has: {user_permissions}")
            return None
        
        # Check if user has at least one required permission
        has_permission = bool(set(required_permissions) & set(user_permissions))
        
        if not has_permission:
            logger.warning(
                f"Permission denied. Required (any): {required_permissions}, "
                f"User has: {user_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required (any): {', '.join(required_permissions)}"
            )
        
        logger.debug(f"Permission check passed. User has: {user_permissions}")
        return None
    
    return permission_checker

