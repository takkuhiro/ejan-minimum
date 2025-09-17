"""
Response models for EJAN API.

This module contains Pydantic models for API responses,
including style generation results and tutorial data.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class GeneratedStyle(BaseModel):
    """Model for a single generated style."""

    id: str = Field(
        ...,
        description="Unique identifier for the style",
    )
    title: str = Field(
        ...,
        description="Title of the style",
    )
    description: str = Field(
        ...,
        description="Description of the style",
    )
    image_url: str = Field(
        ..., description="URL to the generated style image", alias="imageUrl"
    )

    model_config = {"populate_by_name": True}

    @field_validator("image_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that image_url is a valid URL."""
        # Simple URL validation - check if it starts with http/https
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Invalid URL format")

        # Additional validation for URL structure
        try:
            # Basic URL structure check
            parts = v.split("://")
            if len(parts) != 2:
                raise ValueError("Invalid URL format")

            protocol, rest = parts
            if protocol not in ["http", "https"]:
                raise ValueError("URL must use http or https protocol")

            # Check for domain
            if "/" in rest:
                domain = rest.split("/")[0]
            else:
                domain = rest

            if not domain or "." not in domain:
                raise ValueError("Invalid URL domain")

            return v
        except Exception:
            raise ValueError("Invalid URL format")


class GenerateStylesResponse(BaseModel):
    """Response model for styles generation endpoint."""

    styles: List[GeneratedStyle] = Field(
        ...,
        min_length=1,
        description="List of generated styles",
    )

    @field_validator("styles")
    @classmethod
    def validate_styles(cls, v: List[GeneratedStyle]) -> List[GeneratedStyle]:
        """Validate that styles list is not empty."""
        if not v:
            raise ValueError("Styles list cannot be empty")
        return v


class TutorialStep(BaseModel):
    """Model for a single tutorial step."""

    step_number: int = Field(
        ...,
        gt=0,
        description="Step number (must be positive)",
    )
    title: str = Field(
        ...,
        description="Title of the step",
    )
    description: str = Field(
        ...,
        description="Detailed description of the step",
    )
    image_url: str = Field(
        ...,
        description="URL to the step completion image",
    )
    video_url: str = Field(
        ...,
        description="URL to the step instruction video",
    )
    tools: List[str] = Field(
        default_factory=list,
        description="List of tools required for this step",
    )

    @field_validator("image_url", "video_url")
    @classmethod
    def validate_urls(cls, v: str) -> str:
        """Validate that URLs are valid."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Invalid URL format")
        return v


class TutorialResponse(BaseModel):
    """Response model for tutorial generation endpoint."""

    id: str = Field(
        ...,
        description="Unique identifier for the tutorial",
    )
    title: str = Field(
        ...,
        description="Title of the tutorial",
    )
    description: str = Field(
        ...,
        description="Description of the tutorial",
    )
    total_steps: int = Field(
        ...,
        gt=0,
        description="Total number of steps",
    )
    steps: List[TutorialStep] = Field(
        ...,
        description="List of tutorial steps",
    )

    @model_validator(mode="after")
    def validate_total_steps(self) -> "TutorialResponse":
        """Validate that total_steps matches the length of steps list."""
        if self.total_steps != len(self.steps):
            raise ValueError(
                f"total_steps ({self.total_steps}) must match the number of steps ({len(self.steps)})"
            )
        return self


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: str = Field(
        ...,
        description="Error type or code",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
    )
