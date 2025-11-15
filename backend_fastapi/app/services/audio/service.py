"""Audio file service - application layer."""
import os
from typing import List, Tuple, Optional, TYPE_CHECKING
from fastapi import UploadFile, HTTPException, status
from loguru import logger

from app.core.database.interfaces import IFileManager
from app.schemas.audio.models import AudioFile
from app.schemas.audio import AudioFileResponse, AudioPlayResponse
from app.core.config import settings
from app.utils.audio_validation import validate_audio_file
from app.utils.id_utils import generate_file_id

if TYPE_CHECKING:
    from app.services.storage.interfaces import IStorageService
    from app.services.audio.interfaces import IAudioService


class AudioService:
    """Service layer for handling audio file operations.
    
    Implements IAudioService Protocol for audio file operations.
    This class provides the implementation of the audio service interface.
    
    Note: Python Protocols use structural typing (duck typing), so this class
    automatically implements IAudioService if it has matching method signatures.
    The required method (delete_all_user_files) is implemented.
    
    The IAudioService import above documents the Protocol relationship for
    type checkers and IDEs, even though explicit inheritance is not required.
    """
    
    def __init__(
        self,
        file_manager: IFileManager,
        storage_service: "IStorageService"
    ):
        """Initialize with file manager and storage service via dependency injection."""
        self.file_manager = file_manager
        self.storage_service = storage_service
    
    async def list_all_files(self, skip: int = 0, limit: int = 100) -> List[AudioFileResponse]:
        """Get all files."""
        files, total_count = await self.file_manager.find_all(
            skip=skip,
            limit=limit
        )
        
        return [
            AudioFileResponse(
                id=file.id,
                file_name=file.file_name,
                file_url=file.file_url,
                file_type=file.file_type,
                file_metadata=file.file_metadata,
                created_at=file.created_at
            )
            for file in files
        ]
    
    async def get_file_for_playback(
        self,
        file_id: str
    ) -> AudioPlayResponse:
        """Get signed URL for file playback."""
        # Find file by ID
        file = await self.file_manager.find_by_id(file_id)
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Generate signed URL (expires in 1 hour)
        signed_url = await self.storage_service.generate_signed_url(
            file_url=file.file_url,
            expiration_seconds=3600
        )
        
        return AudioPlayResponse(
            signed_url=signed_url,
            expires_in=3600
        )
    
    async def upload_file(
        self,
        file: UploadFile,
    ) -> AudioFileResponse:
        """Upload file to cloud storage and save metadata in database.
        
        Validates file type, extension, and size before upload.
        Generates file_id before upload to ensure S3 key matches database file_id.
        
        Args:
            file: The file to upload
        """
        # Comprehensive validation (MIME type, extension, size)
        is_valid, error_message = validate_audio_file(
            file=file,
            max_size_bytes=settings.MAX_AUDIO_FILE_SIZE_BYTES
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message or "File validation failed"
            )
        
        # Read file content and validate size
        file_content = await file.read()
        file_size = len(file_content)
        
        # Double-check size after reading (in case file.size wasn't available)
        if file_size > settings.MAX_AUDIO_FILE_SIZE_BYTES:
            max_size_mb = settings.MAX_AUDIO_FILE_SIZE_MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        
        # Generate file_id BEFORE uploading to S3
        # This ensures S3 key matches database file_id
        file_id = generate_file_id()
        
        # Upload to cloud storage
        try:
            file_url = await self.storage_service.upload_file(
                file_content=file_content,
                file_name=file.filename or "unknown",
                file_id=file_id,
                content_type=file.content_type
            )
        except Exception as e:
            logger.error(f"Error uploading file to storage: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
        
        # Create file metadata
        file_metadata = {
            "size": file_size,
            "content_type": file.content_type
        }
        
        # Create audio file record with pre-generated file_id
        audio_file = AudioFile(
            id=file_id,  # Use the file_id we generated before upload
            file_type=file.content_type,
            file_name=file.filename or "unknown",
            file_url=file_url,
            file_metadata=file_metadata
        )
        
        # Save to database (will use the provided file_id)
        created_file = await self.file_manager.create(audio_file)
        
        logger.info(f"File uploaded successfully: {created_file.id}")
        
        return AudioFileResponse(
            id=created_file.id,
            file_name=created_file.file_name,
            file_url=created_file.file_url,
            file_type=created_file.file_type,
            file_metadata=created_file.file_metadata,
            created_at=created_file.created_at
        )
    
    async def update_file(
        self,
        file_id: str,
        file_name: Optional[str] = None
    ) -> AudioFileResponse:
        """Update file metadata."""
        # Find file by ID
        file = await self.file_manager.find_by_id(file_id)
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Update file name if provided
        if file_name is not None:
            # Validate that file extension matches original file
            original_ext = os.path.splitext(file.file_name)[1].lower()
            new_ext = os.path.splitext(file_name)[1].lower()
            
            if original_ext != new_ext:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File extension must match original file. Original extension: {original_ext}, provided: {new_ext}"
                )
            
            file.file_name = file_name
        
        # Save updated file
        updated_file = await self.file_manager.save(file)
        
        logger.info(f"Updated file {file_id}")
        
        return AudioFileResponse(
            id=updated_file.id,
            file_name=updated_file.file_name,
            file_url=updated_file.file_url,
            file_type=updated_file.file_type,
            file_metadata=updated_file.file_metadata,
            created_at=updated_file.created_at
        )
    
    async def delete_file(
        self,
        file_id: str
    ) -> bool:
        """Delete file from S3 and database."""
        # Find file by ID
        file = await self.file_manager.find_by_id(file_id)
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete from S3 storage
        try:
            deleted_from_s3 = await self.storage_service.delete_file(file.file_url)
            if not deleted_from_s3:
                logger.warning(f"Failed to delete file from S3: {file.file_url}, but continuing with database deletion")
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            # Continue with database deletion even if S3 deletion fails
            # This prevents orphaned database records
        
        # Delete from database
        deleted_from_db = await self.file_manager.delete(file_id)
        
        if deleted_from_db:
            logger.info(f"Deleted file {file_id}")
            return True
        else:
            logger.error(f"Failed to delete file {file_id} from database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file from database"
            )

