"""User domain model."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class User(BaseModel):
    """User domain entity."""
    id: Optional[str] = Field(None, description="User unique identifier")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    email: str = Field(..., description="User's email address (unique)")
    hashed_password: str = Field(..., description="Hashed password")
    permissions: List[str] = Field(default_factory=list, description="User permissions list")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for database storage."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "permissions": self.permissions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        # Handle both _id (from MongoDB) and id fields
        user_id = data.get("_id") or data.get("id")
        # Ensure ID is a string (in case of ObjectId in old data)
        user_id = str(user_id) if user_id else None
        
        return cls(
            id=user_id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            hashed_password=data["hashed_password"],
            permissions=data.get("permissions", []),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )

