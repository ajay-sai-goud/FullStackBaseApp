"""Utility for parsing S3 URLs.

Extracted from StorageService to improve separation of concerns and testability.
"""
from typing import Tuple


class S3UrlParser:
    """Utility class for parsing S3 URLs."""
    
    @staticmethod
    def parse_bucket_and_key(file_url: str, default_bucket: str = "") -> Tuple[str, str]:
        """Parse S3 URL to extract bucket and key.
        
        Args:
            file_url: S3 URL in format "s3://bucket/key" or just a key string
            default_bucket: Default bucket name if URL doesn't contain bucket
            
        Returns:
            Tuple of (bucket, key)
            
        Examples:
            >>> S3UrlParser.parse_bucket_and_key("s3://my-bucket/path/to/file.mp3", "my-bucket")
            ('my-bucket', 'path/to/file.mp3')
            >>> S3UrlParser.parse_bucket_and_key("path/to/file.mp3", "my-bucket")
            ('my-bucket', 'path/to/file.mp3')
        """
        if file_url.startswith("s3://"):
            # Format: s3://bucket/key
            parts = file_url.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
        else:
            # Assume it's already a key
            bucket = default_bucket
            key = file_url
        
        return bucket, key

