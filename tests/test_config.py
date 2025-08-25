"""Test the configuration module."""

import pytest
from oatie.core.config import Settings


def test_settings_creation():
    """Test that settings can be created successfully."""
    settings = Settings()
    assert settings.PROJECT_NAME == "Oatie AI Reporting"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"


def test_settings_cors_origins():
    """Test CORS origins configuration."""
    settings = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:5173")
    assert len(settings.BACKEND_CORS_ORIGINS) == 2


def test_settings_cors_origins_invalid():
    """Test CORS origins with invalid input."""
    with pytest.raises(ValueError):
        Settings(BACKEND_CORS_ORIGINS=123)


def test_settings_database_url():
    """Test database URL configuration."""
    settings = Settings()
    assert settings.DATABASE_URL == "sqlite:///./oatie.db"


def test_settings_secret_key():
    """Test secret key configuration."""
    settings = Settings()
    assert settings.SECRET_KEY == "your-secret-key-change-in-production"


def test_settings_ai_configuration():
    """Test AI configuration."""
    settings = Settings()
    assert settings.AI_MODEL == "gpt-3.5-turbo"
    assert settings.OPENAI_API_KEY is None


def test_settings_oracle_configuration():
    """Test Oracle BI Publisher configuration."""
    settings = Settings()
    assert settings.BI_PUBLISHER_URL is None
    assert settings.BI_PUBLISHER_USERNAME is None
    assert settings.BI_PUBLISHER_PASSWORD is None