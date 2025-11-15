"""Protocol interfaces for database managers.

These interfaces enable dependency inversion - services depend on abstractions
rather than concrete implementations, improving testability and flexibility.
"""
from typing import Protocol, Optional, List, Tuple

from app.schemas.user.models import User
from app.schemas.audio.models import AudioFile


class IUserManager(Protocol):
    """Protocol interface for user database operations."""
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        ...
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        ...
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
        """Find all users with pagination. Returns (users, total_count)."""
        ...
    
    async def save(self, user: User) -> User:
        """Save or update user."""
        ...
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        ...
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        ...
    
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        ...


class IFileManager(Protocol):
    """Protocol interface for file database operations."""
    
    async def find_by_id(self, file_id: str) -> Optional[AudioFile]:
        """Find file by ID."""
        ...
    
    async def find_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AudioFile], int]:
        """Find all files for a user with pagination. Returns (files, total_count)."""
        ...
    
    async def find_by_user_and_file_id(
        self,
        user_id: str,
        file_id: str
    ) -> Optional[AudioFile]:
        """Find file by user ID and file ID (for ownership verification)."""
        ...
    
    async def save(self, audio_file: AudioFile) -> AudioFile:
        """Save or update file."""
        ...
    
    async def create(self, audio_file: AudioFile) -> AudioFile:
        """Create a new file record."""
        ...
    
    async def delete(self, file_id: str) -> bool:
        """Delete file by ID."""
        ...

