from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = ConfigDict(env_file=".env")
    
    # Database configuration
    database_url: str = "sqlite+aiosqlite:///./oatie.db"
    
    # Oracle connection (for future use)
    oracle_user: Optional[str] = None
    oracle_password: Optional[str] = None
    oracle_dsn: Optional[str] = None
    
    # AI/LLM configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 500
    
    # Application settings
    debug: bool = False
    log_level: str = "INFO"

settings = Settings()

def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
