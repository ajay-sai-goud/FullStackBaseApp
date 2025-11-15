"""Protocol interface for audio service operations.

This interface enables dependency inversion - services depend on abstractions
rather than concrete implementations, improving testability and flexibility.
"""
from typing import Protocol, List, Optional, TYPE_CHECKING
from fastapi import UploadFile

if TYPE_CHECKING:
    from app.schemas.audio import AudioFileResponse, AudioPlayResponse


class IAudioService(Protocol):
    """Protocol interface for audio file service operations."""
    
    async def list_all_files(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List["AudioFileResponse"]:
        """Get all files.
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of AudioFileResponse objects
        """
        ...
    
    async def get_file_for_playback(
        self,
        file_id: str
    ) -> "AudioPlayResponse":
        """Get signed URL for file playback.
        
        Args:
            file_id: The ID of the file to get playback URL for
            
        Returns:
            AudioPlayResponse with signed_url and expires_in
            
        Raises:
            HTTPException: If file not found
        """
        ...
    
    async def upload_file(
        self,
        file: UploadFile
    ) -> "AudioFileResponse":
        """Upload file to cloud storage and save metadata in database.
        
        Validates file type, extension, and size before upload.
        Generates file_id before upload to ensure S3 key matches database file_id.
        
        Args:
            file: The audio file to upload
            
        Returns:
            AudioFileResponse with file details
            
        Raises:
            HTTPException: If validation fails or upload fails
        """
        ...
    
    async def update_file(
        self,
        file_id: str,
        file_name: Optional[str] = None
    ) -> "AudioFileResponse":
        """Update file metadata.
        
        Args:
            file_id: The ID of the file to update
            file_name: Optional new filename for the audio file
            
        Returns:
            AudioFileResponse with updated file details
            
        Raises:
            HTTPException: If file not found
        """
        ...
    
    async def delete_file(
        self,
        file_id: str
    ) -> bool:
        """Delete file from S3 and database.
        
        Args:
            file_id: The ID of the file to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If file not found or deletion fails
        """
        ...

