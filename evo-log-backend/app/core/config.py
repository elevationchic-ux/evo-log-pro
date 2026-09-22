"""
Configuration settings for EVO-LOG EM-ERP
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "EVO-LOG EM-ERP"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./kamlog_erp.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = ""
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
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def model_post_init(self, __context: object) -> None:
        environment = self.ENVIRONMENT.lower()
        if not self.SECRET_KEY and environment in {"development", "dev", "test", "testing"}:
            self.SECRET_KEY = secrets.token_urlsafe(48)
        if environment not in {"production", "prod"}:
            return
        if self.DEBUG:
            raise ValueError("DEBUG must be false in production")
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError("A strong SECRET_KEY is required in production")
        if not self.BACKEND_CORS_ORIGINS or any(
            origin == "*" or "localhost" in origin or "127.0.0.1" in origin
            for origin in self.BACKEND_CORS_ORIGINS
        ):
            raise ValueError("Production CORS origins must be explicit and non-local")
        if self.DATABASE_URL.startswith("sqlite"):
            raise ValueError("SQLite is not supported in production")
        if self.MINIO_ENABLED and (
            self.MINIO_ACCESS_KEY == "minioadmin"
            or self.MINIO_SECRET_KEY == "minioadmin"
        ):
            raise ValueError("Default MinIO credentials are not allowed in production")


settings = Settings()