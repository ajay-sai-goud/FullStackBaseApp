"""Protocol interface for authentication service operations.

This interface enables dependency inversion - services depend on abstractions
rather than concrete implementations, improving testability and flexibility.
"""
from typing import Protocol


class IAuthService(Protocol):
    """Protocol interface for authentication service operations."""
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT token with permissions.
        
        Args:
            email: User's email address
            password: User's plain text password
            
        Returns:
            Dictionary with access_token and token_type
            
        Raises:
            HTTPException: If authentication fails (invalid email or password)
        """
        ...

