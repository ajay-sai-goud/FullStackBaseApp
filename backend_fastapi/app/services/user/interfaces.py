"""Protocol interface for user service operations.

This interface enables dependency inversion - services depend on abstractions
rather than concrete implementations, improving testability and flexibility.
"""
from typing import Protocol, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserCreate, UserUpdate, UserDisplay


class IUserService(Protocol):
    """Protocol interface for user service operations."""
    
    async def create_user(self, user_data: "UserCreate") -> "UserDisplay":
        """Creates a new user after validating and hashing password.
        
        Args:
            user_data: User creation data including email, password, name, and permissions
            
        Returns:
            UserDisplay with created user details
            
        Raises:
            HTTPException: If user with email already exists
        """
        ...
    
    async def list_users(self, skip: int = 0, limit: int = 20) -> List["UserDisplay"]:
        """List all users with pagination.
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of UserDisplay objects
        """
        ...
    
    async def get_user(self, user_id: str) -> "UserDisplay":
        """Get a user by ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            UserDisplay with user details
            
        Raises:
            HTTPException: If user not found
        """
        ...
    
    async def update_user(self, user_id: str, user_data: "UserUpdate") -> "UserDisplay":
        """Update a user by ID.
        
        Args:
            user_id: The unique identifier of the user to update
            user_data: User update data (all fields optional)
            
        Returns:
            UserDisplay with updated user details
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        ...
    
    async def delete_user(self, user_id: str) -> None:
        """Delete a user by ID and all associated audio files.
        
        Args:
            user_id: The unique identifier of the user to delete
            
        Raises:
            HTTPException: If user not found or deletion fails
        """
        ...

