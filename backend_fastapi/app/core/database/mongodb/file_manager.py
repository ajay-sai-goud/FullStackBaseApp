"""FileManager for MongoDB database operations."""
from typing import Optional, List, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.schemas.audio.models import AudioFile
from app.utils.id_utils import generate_file_id
from app.core.database.interfaces import IFileManager


class FileManager:
    """FileManager for MongoDB database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize with database instance."""
        self.collection = db["files"]
    
    async def find_by_id(self, file_id: str) -> Optional[AudioFile]:
        """Find file by ID."""
        try:
            doc = await self.collection.find_one({"_id": file_id})
            if doc:
                return AudioFile.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error finding file by ID {file_id}: {e}")
            return None
    
    async def find_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AudioFile], int]:
        """Find all files for a user with pagination. Returns (files, total_count)."""
        try:
            # Use aggregation pipeline with $facet for count + data in single query
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$facet": {
                    "data": [
                        {"$sort": {"created_at": -1}},
                        {"$skip": skip},
                        {"$limit": limit}
                    ],
                    "count": [{"$count": "total"}]
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(1)
            
            if not result or not result[0]:
                return [], 0
            
            files_data = result[0].get("data", [])
            count_data = result[0].get("count", [])
            total_count = count_data[0]["total"] if count_data else 0
            
            files = [AudioFile.from_dict(doc) for doc in files_data]
            return files, total_count
        except Exception as e:
            logger.error(f"Error finding files for user {user_id}: {e}")
            return [], 0
    
    async def find_by_user_and_file_id(
        self,
        user_id: str,
        file_id: str
    ) -> Optional[AudioFile]:
        """Find file by user ID and file ID (for ownership verification)."""
        try:
            doc = await self.collection.find_one({
                "_id": file_id,
                "user_id": user_id
            })
            if doc:
                return AudioFile.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error finding file {file_id} for user {user_id}: {e}")
            return None
    
    async def save(self, audio_file: AudioFile) -> AudioFile:
        """Save or update file."""
        audio_file.updated_at = datetime.utcnow()
        file_dict = audio_file.to_dict()
        
        if audio_file.id:
            # Update existing file
            file_dict["_id"] = audio_file.id
            file_dict.pop("id", None)
            await self.collection.update_one(
                {"_id": audio_file.id},
                {"$set": file_dict}
            )
            return audio_file
        else:
            # Create new file
            audio_file.id = generate_file_id()
            file_dict["_id"] = audio_file.id
            file_dict.pop("id", None)
            await self.collection.insert_one(file_dict)
            return audio_file
    
    async def create(self, audio_file: AudioFile) -> AudioFile:
        """Create a new file record.
        
        If audio_file.id is already set, uses that ID (for consistency with S3 keys).
        Otherwise, generates a new file_id.
        """
        # Use provided file_id if available, otherwise generate new one
        if not audio_file.id:
            audio_file.id = generate_file_id()
        
        audio_file.created_at = datetime.utcnow()
        audio_file.updated_at = datetime.utcnow()
        file_dict = audio_file.to_dict()
        file_dict["_id"] = audio_file.id
        file_dict.pop("id", None)
        
        await self.collection.insert_one(file_dict)
        logger.info(f"Created file with ID: {audio_file.id}")
        return audio_file
    
    async def delete(self, file_id: str) -> bool:
        """Delete file by ID."""
        try:
            result = await self.collection.delete_one({"_id": file_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False

