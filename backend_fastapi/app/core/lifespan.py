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
from app.utils.id_utils import generate_deterministic_user_id
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
    
    # Get database for all workers
    db = DatabaseManager.get_database()

    # Create default admin user if it doesn't exist (idempotent - safe for concurrent workers)
    # Use deterministic UUID based on email so all workers generate the same ID
    # This ensures MongoDB's _id unique constraint prevents duplicates
    user_manager: IUserManager = _get_user_manager_for_startup(db)
    
    # Generate deterministic ID for admin user based on email
    # This ensures all workers try to create the same _id, so only one succeeds
    admin_id = generate_deterministic_user_id(settings.ADMIN_EMAIL)
    
    try:
        admin_user = User(
            id=admin_id,  # Set deterministic ID before creation
            first_name="Admin",
            last_name="User",
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            permissions=Permissions.ALL_PERMISSIONS,
        )
        await user_manager.create(admin_user)
        logger.info(f"Default admin user created: {settings.ADMIN_EMAIL} (ID: {admin_id})")
    except Exception as e:
        # Check if it's a duplicate key error (E11000) - means admin already exists
        error_str = str(e)
        if "E11000" in error_str or "duplicate key" in error_str.lower():
            # Admin user already exists (either from previous startup or created by another worker)
            # This is expected and fine - the operation is idempotent
            logger.debug(f"Default admin user already exists: {settings.ADMIN_EMAIL} (ID: {admin_id})")
        else:
            # Some other error occurred - log as warning but don't fail startup
            logger.warning(f"Unexpected error creating default admin user: {e}")
    
    # Create indexes (idempotent - safe to run multiple times)
    try:
        # User collection indexes
        users_collection = db["users"]
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("created_at")
        logger.info("Created indexes for users collection")
        
        # Files collection indexes
        files_collection = db["files"]
        await files_collection.create_index("created_at")
        logger.info("Created indexes for files collection")
    except Exception as e:
        logger.warning(f"Error creating indexes (may already exist): {e}")
    
    # Store database in app state
    app.state.db = db
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")
    DatabaseManager.close_connection()

