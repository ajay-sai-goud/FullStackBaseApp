import os
from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Boilerplate")
    
    # Logging configuration
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOGURU_JSON_LOGS: bool = os.getenv("LOGURU_JSON_LOGS", False)

    # OpenTelemetry configuration
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "fastapi-boilerplate")
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_DEBUG_LOG_SPANS: bool = os.getenv("OTEL_DEBUG_LOG_SPANS", False)

    # CORS configuration
    ALLOWED_ORIGINS: str = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]
    ALLOWED_METHODS: str = [method.strip() for method in os.getenv("ALLOWED_METHODS", "*").split(",")]
    ALLOWED_HEADERS: str = [header.strip() for header in os.getenv("ALLOWED_HEADERS", "*").split(",")]

    # Database configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "app_db")
    
    # JWT configuration (RS256)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    # JWT Issuer (iss) - single string identifying who issued the token
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "https://localhost:8000/")
    # JWT Audience (aud) - comma-separated string that becomes an array in the token
    # Example: "https://app1.com/,https://app2.com/" becomes ["https://app1.com/", "https://app2.com/"]
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "https://localhost:3000/")
    # RSA Private Key (for signing tokens) - can be file path or PEM string
    JWT_PRIVATE_KEY_PATH: str | None = os.getenv("JWT_PRIVATE_KEY_PATH")
    JWT_PRIVATE_KEY: str | None = os.getenv("JWT_PRIVATE_KEY")
    # RSA Public Key (for verifying tokens) - can be file path or PEM string
    JWT_PUBLIC_KEY_PATH: str | None = os.getenv("JWT_PUBLIC_KEY_PATH")
    JWT_PUBLIC_KEY: str | None = os.getenv("JWT_PUBLIC_KEY")
    
    # AWS S3 configuration
    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME: str | None = os.getenv("S3_BUCKET_NAME")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Audio file upload configuration
    MAX_AUDIO_FILE_SIZE_MB: int = int(os.getenv("MAX_AUDIO_FILE_SIZE_MB", "100"))
    
    @property
    def MAX_AUDIO_FILE_SIZE_BYTES(self) -> int:
        """Convert MAX_AUDIO_FILE_SIZE_MB to bytes."""
        return self.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024

    # Default Admin User
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@password123")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()