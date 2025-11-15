"""Audio file request/response schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.validators import validate_file_id


class AudioFileResponse(BaseModel):
    """Response schema for audio file data."""
    id: str = Field(..., description="File unique identifier")
    file_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="Cloud storage URL")
    file_type: str = Field(..., description="MIME type of the file")
    file_metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata")
    created_at: datetime = Field(..., description="Creation timestamp")


class AudioFileListResponse(BaseModel):
    """Response schema for list of audio files."""
    files: list[AudioFileResponse] = Field(..., description="List of audio files")


class AudioPlayResponse(BaseModel):
    """Response schema for audio playback URL."""
    signed_url: str = Field(..., description="Signed URL for audio playback")
    expires_in: int = Field(..., description="URL expiration time in seconds")


class AudioFileIdPathParams(BaseModel):
    """Path parameters for audio file ID."""
    id: str = Field(..., min_length=1, description="File ID")
    
    # Use centralized file ID validator
    @field_validator('id', mode='before')
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """Validate file ID using centralized validator."""
        if v is None:
            raise ValueError("File ID is required and cannot be null")
        if not isinstance(v, str):
            raise ValueError("File ID must be a string")
        v = v.strip()
        if not v:
            raise ValueError("File ID cannot be empty or whitespace only")
        return validate_file_id(v, strict=False)


class AudioFileListQueryParams(BaseModel):
    """Query parameters for listing audio files."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=100, description="Maximum number of records to return")


class AudioFileUpdate(BaseModel):
    """Request schema for updating audio file metadata."""
    file_name: Optional[str] = Field(None, min_length=1, max_length=255, description="New filename for the audio file")
    
    @field_validator('file_name', mode='before')
    @classmethod
    def validate_file_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate file name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("File name cannot be empty")
            if len(v) > 255:
                raise ValueError("File name cannot exceed 255 characters")
        return v

