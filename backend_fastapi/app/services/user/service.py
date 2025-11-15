"""User domain service - application layer."""
from typing import List, TYPE_CHECKING
from loguru import logger
from opentelemetry import trace
from fastapi import HTTPException, status

from app.schemas.user import UserCreate, UserUpdate, UserDisplay
from app.core.database.interfaces import IUserManager
from app.schemas.user.models import User
from app.utils.password import hash_password
from app.core.constants import DEFAULT_USER_PERMISSIONS, Permissions

if TYPE_CHECKING:
    from app.services.audio.interfaces import IAudioService

tracer = trace.get_tracer(__name__)


class UserService:
    """
    Service layer for handling user-related business logic.
    """
    
    def __init__(
        self,
        user_manager: IUserManager,
        audio_service: "IAudioService" = None
    ):
        """Initialize with user manager and audio service via dependency injection."""
        self.user_manager = user_manager
        self.audio_service = audio_service

    async def create_user(self, user_data: UserCreate) -> UserDisplay:
        """
        Creates a new user after validating and hashing password.
        """
        with tracer.start_as_current_span("user_service_create") as span:
            span.set_attribute("user.email", user_data.email)

            # Check if user with email already exists
            existing_user = await self.user_manager.find_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists."
                )

            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Initialize permissions (use provided or default)
            permissions = user_data.permissions if user_data.permissions is not None else DEFAULT_USER_PERMISSIONS.copy()
            
            # Ensure read:audio is always included (required permission)
            if Permissions.READ_AUDIO not in permissions:
                permissions.append(Permissions.READ_AUDIO)
            
            # Create user model
            new_user = User(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                hashed_password=hashed_password,
                permissions=permissions
            )

            # Save to database
            logger.info(f"Creating user '{user_data.email}' in the database.")
            created_user = await self.user_manager.create(new_user)

            span.set_attribute("user.id", created_user.id)
            logger.info(f"User '{created_user.email}' created successfully with ID {created_user.id}.")

            return UserDisplay(
                id=created_user.id,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                email=created_user.email,
                permissions=created_user.permissions,
                created_at=created_user.created_at,
                updated_at=created_user.updated_at
            )

    async def list_users(self, skip: int = 0, limit: int = 20) -> List[UserDisplay]:
        """List all users with pagination."""
        with tracer.start_as_current_span("user_service_list") as span:
            span.set_attribute("pagination.skip", skip)
            span.set_attribute("pagination.limit", limit)
            
            users, total_count = await self.user_manager.find_all(skip=skip, limit=limit)
            
            span.set_attribute("users.total_count", total_count)
            logger.info(f"Listed {len(users)} users (total: {total_count})")
            
            return [
                UserDisplay(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    permissions=user.permissions,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                for user in users
            ]

    async def get_user(self, user_id: str) -> UserDisplay:
        """Get a user by ID."""
        with tracer.start_as_current_span("user_service_get") as span:
            span.set_attribute("user.id", user_id)
            
            user = await self.user_manager.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return UserDisplay(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                permissions=user.permissions,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserDisplay:
        """Update a user by ID."""
        with tracer.start_as_current_span("user_service_update") as span:
            span.set_attribute("user.id", user_id)
            
            # Get existing user
            existing_user = await self.user_manager.find_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if email is being updated and if it's already taken
            if user_data.email and user_data.email != existing_user.email:
                email_user = await self.user_manager.find_by_email(user_data.email)
                if email_user:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already exists"
                    )
            
            # Update fields
            update_dict = user_data.model_dump(exclude_unset=True)
            
            if "password" in update_dict:
                # Hash new password
                update_dict["hashed_password"] = hash_password(update_dict.pop("password"))
            
            # Handle permissions update - ensure read:audio is always included
            if "permissions" in update_dict:
                permissions = update_dict["permissions"]
                # Ensure read:audio is always included (required permission)
                if Permissions.READ_AUDIO not in permissions:
                    permissions.append(Permissions.READ_AUDIO)
                update_dict["permissions"] = permissions
            
            # Update user model
            for key, value in update_dict.items():
                setattr(existing_user, key, value)
            
            # Final check: ensure read:audio is in permissions after update
            if Permissions.READ_AUDIO not in existing_user.permissions:
                existing_user.permissions.append(Permissions.READ_AUDIO)
            
            # Save to database
            updated_user = await self.user_manager.update(existing_user)
            
            logger.info(f"Updated user with ID: {updated_user.id}")
            
            return UserDisplay(
                id=updated_user.id,
                first_name=updated_user.first_name,
                last_name=updated_user.last_name,
                email=updated_user.email,
                permissions=updated_user.permissions,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
            )

    async def delete_user(self, user_id: str) -> None:
        """Delete a user by ID."""
        with tracer.start_as_current_span("user_service_delete") as span:
            span.set_attribute("user.id", user_id)
            
            # Check if user exists
            user = await self.user_manager.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Delete user from database
            # Note: Files are now shared and not tied to users, so no need to delete files
            deleted = await self.user_manager.delete(user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete user"
                )
            
            logger.info(f"Deleted user with ID: {user_id}")

