"""User-related API endpoints."""
from fastapi import APIRouter, status, Depends, Path as PathParam, Body
from loguru import logger

from app.schemas.user import UserCreate, UserUpdate, UserDisplay, UserListQueryParams, UserIdPathParams, PermissionsResponse
from app.services.user.interfaces import IUserService
from app.core.observability import TracingAPIRoute
from app.core.dependencies import get_user_service, require_auth, require_permissions
from app.core.constants import Permissions
from app.schemas.user.models import User

router = APIRouter(route_class=TracingAPIRoute, prefix="/users", tags=["Users"])


@router.get(
    "/permissions",
    response_model=PermissionsResponse,
    status_code=status.HTTP_200_OK,
)
async def list_permissions(
    current_user: User = Depends(require_auth)
) -> PermissionsResponse:
    """
    Get list of all available permissions in the system.
    
    Returns a list of all valid permissions that can be assigned to users.
    
    **Available Permissions:**
    - `read:audio` - Read audio files
    - `write:audio` - Upload audio files
    - `delete:audio` - Delete audio files
    - `read:user` - Read user information
    - `write:user` - Create/update users
    - `delete:user` - Delete users
    - `admin` - Full administrative access (grants all permissions)
    
    **Required:** Authentication (any authenticated user can view permissions)
    """
    logger.info(f"User {current_user.id} requesting permissions list")
    return PermissionsResponse(permissions=Permissions.ALL_PERMISSIONS)


@router.post(
    "",
    response_model=UserDisplay,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.WRITE_USER)),
    user_service: IUserService = Depends(get_user_service)
) -> UserDisplay:
    """
    Create a new user.
    
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **email**: User's email address (must be unique)
    - **password**: User's password (min 6 chars, must contain: 1 uppercase, 1 lowercase, 1 number, 1 special char)
    - **confirm_password**: Password confirmation (must match password)
    - **permissions**: (Optional) List of permissions for the user. If not provided, defaults to ['read:audio', 'write:audio']
    
    **Available Permissions:**
    - `read:audio` - Read audio files
    - `write:audio` - Upload audio files
    - `delete:audio` - Delete audio files
    - `read:user` - Read user information
    - `write:user` - Create/update users
    - `delete:user` - Delete users
    - `admin` - Full administrative access (grants all permissions)
    
    **Required Permission:** `write:user` or `admin`
    
    Requires authentication and WRITE_USER permission (admin only).
    """
    logger.info(f"User {current_user.id} creating new user: {user.email}")
    return await user_service.create_user(user)


@router.get(
    "",
    response_model=list[UserDisplay],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    query: UserListQueryParams = Depends(),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.READ_USER)),
    user_service: IUserService = Depends(get_user_service)
) -> list[UserDisplay]:
    """
    List all users with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    
    **Required Permission:** `read:user` or `admin`
    
    Requires authentication and READ_USER permission.
    """
    logger.info(f"User {current_user.id} listing users: skip={query.skip}, limit={query.limit}")
    return await user_service.list_users(skip=query.skip, limit=query.limit)


@router.get(
    "/{user_id}",
    response_model=UserDisplay,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: str = PathParam(..., min_length=1, description="User unique identifier"),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.READ_USER)),
    user_service: IUserService = Depends(get_user_service)
) -> UserDisplay:
    """
    Get a user by ID.
    
    - **user_id**: User's unique identifier
    
    **Required Permission:** `read:user` or `admin`
    
    Requires authentication and READ_USER permission.
    """
    # Validate using schema
    path_params = UserIdPathParams(user_id=user_id)
    logger.info(f"User {current_user.id} getting user: {path_params.user_id}")
    return await user_service.get_user(path_params.user_id)


@router.put(
    "/{user_id}",
    response_model=UserDisplay,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_data: UserUpdate = Body(...),
    user_id: str = PathParam(..., min_length=1, description="User unique identifier"),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.WRITE_USER)),
    user_service: IUserService = Depends(get_user_service)
) -> UserDisplay:
    """
    Update a user by ID.
    
    - **user_id**: User's unique identifier
    - All fields are optional - only provided fields will be updated
    - **password**: If provided, will be hashed before storage
    
    **Required Permission:** `write:user` or `admin`
    
    Requires authentication and WRITE_USER permission.
    """
    # Validate using schema
    path_params = UserIdPathParams(user_id=user_id)
    logger.info(f"User {current_user.id} updating user: {path_params.user_id}")
    return await user_service.update_user(path_params.user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: str = PathParam(..., min_length=1, description="User unique identifier"),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.DELETE_USER)),
    user_service: IUserService = Depends(get_user_service)
) -> None:
    """
    Delete a user by ID.
    
    - **user_id**: User's unique identifier
    
    **Required Permission:** `delete:user` or `admin`
    
    Requires authentication and DELETE_USER permission.
    """
    # Validate using schema
    path_params = UserIdPathParams(user_id=user_id)
    logger.info(f"User {current_user.id} deleting user: {path_params.user_id}")
    await user_service.delete_user(path_params.user_id)

