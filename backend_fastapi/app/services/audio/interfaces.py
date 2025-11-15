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
    
    async def list_user_files(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List["AudioFileResponse"]:
        """Get all files for a user.
        
        Args:
            user_id: The ID of the user whose files to retrieve
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of AudioFileResponse objects
        """
        ...
    
    async def get_file_for_playback(
        self,
        file_id: str,
        user_id: str
    ) -> "AudioPlayResponse":
        """Get signed URL for file playback. Verifies ownership.
        
        Args:
            file_id: The ID of the file to get playback URL for
            user_id: The ID of the user requesting playback (for ownership verification)
            
        Returns:
            AudioPlayResponse with signed_url and expires_in
            
        Raises:
            HTTPException: If file not found or access denied
        """
        ...
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: str
    ) -> "AudioFileResponse":
        """Upload file to cloud storage and save metadata in database.
        
        Validates file type, extension, and size before upload.
        Generates file_id before upload to ensure S3 key matches database file_id.
        
        Args:
            file: The audio file to upload
            user_id: The ID of the user uploading the file
            
        Returns:
            AudioFileResponse with file details
            
        Raises:
            HTTPException: If validation fails or upload fails
        """
        ...
    
    async def update_file(
        self,
        file_id: str,
        user_id: str,
        file_name: Optional[str] = None
    ) -> "AudioFileResponse":
        """Update file metadata. Verifies ownership before allowing update.
        
        Args:
            file_id: The ID of the file to update
            user_id: The ID of the user requesting update (for ownership verification)
            file_name: Optional new filename for the audio file
            
        Returns:
            AudioFileResponse with updated file details
            
        Raises:
            HTTPException: If file not found or access denied
        """
        ...
    
    async def delete_file(
        self,
        file_id: str,
        user_id: str
    ) -> bool:
        """Delete file from S3 and database. Verifies ownership before allowing delete.
        
        Args:
            file_id: The ID of the file to delete
            user_id: The ID of the user requesting delete (for ownership verification)
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If file not found, access denied, or deletion fails
        """
        ...
    
    async def delete_all_user_files(self, user_id: str) -> int:
        """Delete all audio files for a user from S3 and database.
        
        Args:
            user_id: The ID of the user whose files should be deleted
            
        Returns:
            Number of files successfully deleted from the database
            
        Note:
            - Errors during S3 deletion are logged but don't stop the process
            - Errors during database deletion are logged but don't stop the process
            - Returns count of files deleted from database (even if S3 deletion failed)
        """
        ...

