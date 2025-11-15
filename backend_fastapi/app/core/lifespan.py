"""Application lifespan management for startup and shutdown events."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core import settings
from app.core.database.mongodb.user_manager import UserManager
from app.core.database.interfaces import IUserManager
from app.schemas.user.models import User
from app.utils.password import hash_password
from app.core.constants import Permissions


def _get_user_manager_for_startup(db: AsyncIOMotorDatabase) -> IUserManager:
    """Get UserManager instance for startup operations.
    
    This helper function follows the dependency injection pattern used in
    dependencies.py but works in the lifespan context where FastAPI's Depends
    is not available.
    
    Args:
        db: Database instance
        
    Returns:
        IUserManager interface implementation
    """
    return UserManager(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Application startup")
    
    # Validate S3 configuration
    if not settings.S3_BUCKET_NAME:
        logger.warning("S3_BUCKET_NAME is not set. File uploads will fail.")
    
    # Initialize database connection
    from app.core.database.connection import DatabaseManager
    
    # Get database using MONGO_URI from settings
    db = DatabaseManager.get_database()

    # Create default admin user if it doesn't exist
    # Use helper function to maintain DI pattern
    user_manager: IUserManager = _get_user_manager_for_startup(db)
    admin_user = await user_manager.find_by_email(settings.ADMIN_EMAIL)
    if not admin_user:
        admin_user = User(
            first_name="Admin",
            last_name="User",
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            permissions=Permissions.ALL_PERMISSIONS,
        )
        await user_manager.create(admin_user)
        logger.info(f"Default admin user created: {settings.ADMIN_EMAIL}")
    
    # Create indexes
    try:
        # User collection indexes
        users_collection = db["users"]
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("created_at")
        logger.info("Created indexes for users collection")
        
        # Files collection indexes
        files_collection = db["files"]
        await files_collection.create_index("user_id")
        await files_collection.create_index("created_at")
        await files_collection.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("Created indexes for files collection")
    except Exception as e:
        logger.warning(f"Error creating indexes (may already exist): {e}")
    
    # Store database in app state
    app.state.db = db
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")
    DatabaseManager.close_connection()

