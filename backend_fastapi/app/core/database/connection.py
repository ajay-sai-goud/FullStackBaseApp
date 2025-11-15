"""MongoDB connection manager with connection pooling."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from typing import Optional

from app.core.config import settings


class DatabaseManager:
    """Manages MongoDB connection with connection pooling."""
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get or create MongoDB client with connection pooling."""
        if cls._client is None:
            # Simply pass the MONGO_URI directly to AsyncIOMotorClient
            # The URI contains all connection details including authentication
            cls._client = AsyncIOMotorClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                uuidRepresentation="standard",
            )
            logger.info("Created MongoDB connection pool using URI")
        
        return cls._client
    
    @classmethod
    def get_database(cls, database_name: str = None) -> AsyncIOMotorDatabase:
        """Get database instance from client."""
        if database_name is None:
            database_name = settings.MONGO_DB_NAME
            logger.info(f"Using default database: {database_name}")
            
        if cls._database is None:
            client = cls.get_client()
            cls._database = client[database_name]
            logger.info(f"Connected to database: {database_name}")
        
        return cls._database
    
    @classmethod
    def close_connection(cls):
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("Closed MongoDB connection")

