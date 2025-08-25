import os
from typing import Any, Dict, Optional, List
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Oatie AI Reporting"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "oatie"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "oatie_ai"
    POSTGRES_PORT: str = "5432"
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Oracle BI Publisher Integration
    ORACLE_BI_SERVER: Optional[str] = None
    ORACLE_BI_USERNAME: Optional[str] = None
    ORACLE_BI_PASSWORD: Optional[str] = None
    
    # AI/ML Configuration
    OPENAI_API_KEY: Optional[str] = None
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Security
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()