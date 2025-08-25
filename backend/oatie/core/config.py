"""Core application configuration."""

from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, field_validator


class Settings(BaseModel):
    """Application settings."""

    PROJECT_NAME: str = "Oatie AI Reporting"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Assemble CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./oatie.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Oracle BI Publisher
    BI_PUBLISHER_URL: Optional[str] = None
    BI_PUBLISHER_USERNAME: Optional[str] = None
    BI_PUBLISHER_PASSWORD: Optional[str] = None

    # AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-3.5-turbo"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        """Pydantic config."""

        case_sensitive = True
        env_file = ".env"


settings = Settings()
