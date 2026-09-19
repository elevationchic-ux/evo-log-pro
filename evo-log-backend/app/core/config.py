"""
Configuration settings for EVO-LOG EM-ERP
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "EVO-LOG EM-ERP"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./kamlog_erp.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "https://EVO-LOG-erp.cm"]
    
    # MinIO
    MINIO_ENABLED: bool = False
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_DOCUMENTS: str = "documents"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@EVO-LOG.cm"
    
    # WhatsApp
    WHATSAPP_ENABLED: bool = False
    WHATSAPP_API_URL: str = ""
    WHATSAPP_API_KEY: str = ""
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()