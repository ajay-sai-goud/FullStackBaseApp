"""AudioFile domain model."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AudioFile(BaseModel):
    """Audio file domain entity."""
    id: Optional[str] = Field(None, description="File unique identifier")
    file_type: str = Field(..., description="MIME type of the file (e.g., audio/mpeg)")
    file_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="Cloud storage URL or bucket-key reference")
    file_metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata (duration, size, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def to_dict(self) -> dict:
        """Convert audio file to dictionary for database storage."""
        return {
            "id": self.id,
            "file_type": self.file_type,
            "file_name": self.file_name,
            "file_url": self.file_url,
            "file_metadata": self.file_metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AudioFile":
        """Create audio file from dictionary."""
        # Handle both _id (from MongoDB) and id fields
        file_id = data.get("_id") or data.get("id")
        # Ensure ID is a string (in case of ObjectId in old data)
        file_id = str(file_id) if file_id else None
        
        # Note: user_id is ignored if present in old data (for migration compatibility)
        
        return cls(
            id=file_id,
            file_type=data["file_type"],
            file_name=data["file_name"],
            file_url=data["file_url"],
            file_metadata=data.get("file_metadata", {}),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )

