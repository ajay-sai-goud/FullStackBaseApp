"""UserManager for MongoDB database operations."""
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.schemas.user.models import User
from app.utils.id_utils import generate_user_id
from app.core.database.interfaces import IUserManager


class UserManager:
    """UserManager for MongoDB database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize with database instance."""
        self.collection = db["users"]
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        try:
            doc = await self.collection.find_one({"_id": user_id})
            if doc:
                return User.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error finding user by ID {user_id}: {e}")
            return None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                return User.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error finding user by email {email}: {e}")
            return None
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[User], int]:
        """Find all users with pagination. Returns (users, total_count)."""
        try:
            # Use aggregation pipeline with $facet for count + data in single query
            pipeline = [
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
            
            users_data = result[0].get("data", [])
            count_data = result[0].get("count", [])
            total_count = count_data[0]["total"] if count_data else 0
            
            users = [User.from_dict(doc) for doc in users_data]
            return users, total_count
        except Exception as e:
            logger.error(f"Error finding all users: {e}")
            return [], 0
    
    async def save(self, user: User) -> User:
        """Save or update user."""
        user.updated_at = datetime.utcnow()
        user_dict = user.to_dict()
        
        if user.id:
            # Update existing user
            user_dict["_id"] = user.id
            user_dict.pop("id", None)
            await self.collection.update_one(
                {"_id": user.id},
                {"$set": user_dict}
            )
            return user
        else:
            # Create new user
            user.id = generate_user_id()
            user_dict["_id"] = user.id
            user_dict.pop("id", None)
            await self.collection.insert_one(user_dict)
            return user
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        user.id = generate_user_id()
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        user_dict = user.to_dict()
        user_dict["_id"] = user.id
        user_dict.pop("id", None)
        
        await self.collection.insert_one(user_dict)
        logger.info(f"Created user with ID: {user.id}")
        return user
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        if not user.id:
            raise ValueError("User ID is required for update")
        
        user.updated_at = datetime.utcnow()
        user_dict = user.to_dict()
        user_dict.pop("id", None)
        
        await self.collection.update_one(
            {"_id": user.id},
            {"$set": user_dict}
        )
        logger.info(f"Updated user with ID: {user.id}")
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        try:
            result = await self.collection.delete_one({"_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

