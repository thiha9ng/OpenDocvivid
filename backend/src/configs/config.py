import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration class"""
    
    # Application basic configuration
    environment: str = "development"
    debug: bool = True
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API configuration
    api_prefix: str = "/api/v1"
    
    # Google api key
    google_api_key: str = ""
    # Gemini API configuration
    gemini_api_key: str = ""
    
    # Google Cloud Storage configuration
    gcs_bucket_name: str = ""
    gcs_project_id: str = ""
    gcs_credentials_path: Optional[str] = None  # Path to service account JSON file

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None  # If None, only console logging
    log_max_size: int = 10  # Max log file size in MB
    log_backup_count: int = 5  # Number of backup log files
    
     # Database configuration
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "user"
    database_password: str = "password"
    database_name: str = "default"
    database_echo: bool = False  # Set to True for SQL query logging
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_username: str = "default"
    redis_password: str = ""
    redis_db: int = 0

    # Celery configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # jwt
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SECRET_KEY: str = ""

    google_client_id: str = ""

    # payment
    payment_api_key: str = ""
    webhook_secret: str = ""

    
    @property
    def database_url(self) -> str:
        """Generate async database URL from components"""
        # asyncpg uses 'ssl' parameter, not 'sslmode'
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def sync_database_url(self) -> str:
        """Generate sync database URL for Celery tasks"""
        # psycopg2 uses 'sslmode' parameter
        return f"postgresql+psycopg2://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    class Config:
        env_file = ".production.env"

# Global configuration instance
settings = Settings() 