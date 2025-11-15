"""StorageService for S3 cloud storage operations."""
import boto3
import asyncio
from botocore.exceptions import ClientError
from botocore.config import Config
from loguru import logger
from typing import Optional

from app.services.storage.interfaces import IStorageService
from app.utils.s3_url_parser import S3UrlParser


class StorageService:
    """StorageService for S3 cloud storage operations.
    
    Implements IStorageService Protocol for cloud storage operations.
    This class provides S3-specific implementation of the storage interface.
    
    Note: Python Protocols use structural typing (duck typing), so this class
    automatically implements IStorageService if it has matching method signatures.
    All required methods (upload_file, generate_signed_url, delete_file) are implemented.
    
    The IStorageService import above documents the Protocol relationship for
    type checkers and IDEs, even though explicit inheritance is not required.
    """
    
    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        """Initialize S3 client."""
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        if access_key_id and secret_access_key:
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                config=Config(signature_version='s3v4')
            )
        else:
            # Use default credentials (IAM role, environment variables, etc.)
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                config=Config(signature_version='s3v4')
            )
    
    def _generate_file_key(self, user_id: str, file_id: str, file_name: str) -> str:
        """Generate unique S3 key for file using database file_id.
        
        Structure: users/{user_id}/{file_id}/{filename}
        This ensures direct mapping between S3 keys and database file_id.
        """
        # Sanitize filename for S3 key
        safe_filename = file_name.replace(' ', '_').replace('/', '_')
        
        return f"users/{user_id}/{file_id}/{safe_filename}"
    
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        user_id: str,
        file_id: str,
        content_type: str
    ) -> str:
        """Upload file to S3.
        
        Args:
            file_content: File content as bytes
            file_name: Original filename
            user_id: User ID who owns the file
            file_id: Database file ID (must be generated before calling this method)
            content_type: MIME type of the file
            
        Returns:
            S3 URL in format: s3://bucket/key
        """
        try:
            # Generate S3 key using database file_id
            s3_key = self._generate_file_key(user_id, file_id, file_name)
            
            # Upload to S3 (run in thread pool for async)
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            
            # Return S3 URL
            file_url = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"File uploaded to S3: {file_url}")
            
            return file_url
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    async def generate_signed_url(
        self,
        file_url: str,
        expiration_seconds: int = 3600
    ) -> str:
        """Generate signed URL for S3 file."""
        try:
            # Extract bucket and key from S3 URL
            bucket, key = S3UrlParser.parse_bucket_and_key(file_url, self.bucket_name)
            
            # Generate presigned URL (run in thread pool for async)
            signed_url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration_seconds
            )
            
            logger.info(f"Generated signed URL for {key}, expires in {expiration_seconds}s")
            return signed_url
        except ClientError as e:
            logger.error(f"Error generating signed URL: {e}")
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from S3."""
        try:
            # Extract bucket and key from S3 URL
            bucket, key = S3UrlParser.parse_bucket_and_key(file_url, self.bucket_name)
            
            # Delete from S3 (run in thread pool for async)
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=bucket,
                Key=key
            )
            logger.info(f"Deleted file from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False

