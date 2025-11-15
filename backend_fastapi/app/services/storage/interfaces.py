"""Protocol interface for storage service operations.

This interface enables dependency inversion - services depend on abstractions
rather than concrete implementations, improving testability and flexibility.
"""
from typing import Protocol


class IStorageService(Protocol):
    """Protocol interface for cloud storage operations."""
    
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        user_id: str,
        file_id: str,
        content_type: str
    ) -> str:
        """Upload file to cloud storage.
        
        Args:
            file_content: File content as bytes
            file_name: Original filename
            user_id: User ID who owns the file
            file_id: Database file ID (must be generated before calling this method)
            content_type: MIME type of the file
            
        Returns:
            Storage URL (e.g., s3://bucket/key)
        """
        ...
    
    async def generate_signed_url(
        self,
        file_url: str,
        expiration_seconds: int = 3600
    ) -> str:
        """Generate signed URL for file access.
        
        Args:
            file_url: Storage URL (e.g., s3://bucket/key)
            expiration_seconds: URL expiration time in seconds
            
        Returns:
            Presigned URL for file access
        """
        ...
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from cloud storage.
        
        Args:
            file_url: Storage URL (e.g., s3://bucket/key)
            
        Returns:
            True if deletion was successful, False otherwise
        """
        ...

