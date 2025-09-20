"""
Application configuration management.
Loads settings from environment variables.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Required API keys and project settings
    google_api_key: str = Field(
        ..., description="Google API key for Gemini/Nano Banana/Veo3"
    )
    google_cloud_project: str = Field(..., description="Google Cloud Project ID")
    storage_bucket: str = Field(..., description="Google Cloud Storage bucket name")

    # Application settings
    env: str = Field(
        default="development",
        description="Environment (development/staging/production)",
    )
    app_name: str = Field(default="Ejan API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")

    # CORS settings - can be a string (comma-separated) or a list
    cors_origins: Union[List[str], str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",  # Allow extra fields from environment
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == "production"


# Create singleton instance
# Type ignore because Settings loads from environment variables
settings = Settings()  # type: ignore[call-arg]
