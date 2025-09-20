"""
Unit tests for configuration module.
"""

import pytest
from unittest.mock import patch
import os


def test_config_loads_environment_variables():
    """Test that config properly loads environment variables."""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "test-key-123",
            "GOOGLE_CLOUD_PROJECT": "test-project-456",
            "STORAGE_BUCKET": "test-bucket-789",
            "ENV": "development",
        },
    ):
        # Import after setting env vars to test initialization
        from app.core.config import Settings

        settings = Settings()

        assert settings.google_api_key == "test-key-123"
        assert settings.google_cloud_project == "test-project-456"
        assert settings.storage_bucket == "test-bucket-789"
        assert settings.env == "development"


def test_config_has_default_values():
    """Test that config has sensible default values."""
    with patch.dict(os.environ, clear=True):
        # Only set required env vars
        os.environ["GOOGLE_API_KEY"] = "key"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "project"
        os.environ["STORAGE_BUCKET"] = "bucket"

        from app.core.config import Settings

        settings = Settings()

        assert settings.env == "development"  # Should have default
        assert settings.cors_origins is not None  # Should have default CORS origins


def test_config_cors_origins_parsing():
    """Test that CORS origins are properly parsed from string."""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "key",
            "GOOGLE_CLOUD_PROJECT": "project",
            "STORAGE_BUCKET": "bucket",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:3001",
        },
    ):
        from app.core.config import Settings

        settings = Settings()

        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:3001" in settings.cors_origins
        assert len(settings.cors_origins) == 2


def test_config_validation_for_required_fields():
    """Test that config validation fails when required fields are missing."""
    from pydantic import ValidationError

    with patch.dict(os.environ, clear=True):
        # Ensure no .env file is read
        with pytest.raises(ValidationError) as exc_info:
            from app.core.config import Settings

            Settings(_env_file=None)

        # Should fail because required fields are missing
        assert "google_api_key" in str(exc_info.value) or "Field required" in str(
            exc_info.value
        )


def test_config_singleton_pattern():
    """Test that config uses singleton pattern for efficiency."""
    with patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "key",
            "GOOGLE_CLOUD_PROJECT": "project",
            "STORAGE_BUCKET": "bucket",
        },
    ):
        from app.core.config import settings as settings1
        from app.core.config import settings as settings2

        # Should be the same instance
        assert settings1 is settings2
