"""
Request models for EJAN API.

This module contains Pydantic models for validating and serializing
API request data, including photo uploads and tutorial generation requests.
"""

import base64
import binascii
from enum import Enum
from typing import Optional, ClassVar

from pydantic import BaseModel, Field, field_validator


class Gender(str, Enum):
    """Gender options for style generation."""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class PhotoUploadRequest(BaseModel):
    """Request model for photo upload and style generation."""

    # Class-level constants
    MAX_SIZE_MB: ClassVar[int] = 10
    SUPPORTED_FORMATS: ClassVar[tuple[bytes, ...]] = (
        b"\x89PNG",  # PNG
        b"\xff\xd8\xff",  # JPEG
        b"RIFF",  # WebP (partial check)
    )

    photo: str = Field(
        ...,
        description="Base64 encoded image data",
    )
    gender: Gender = Field(
        ...,
        description="Gender selection for style generation",
    )

    @field_validator("photo")
    @classmethod
    def validate_photo(cls, v: str) -> str:
        """Validate base64 encoded photo."""
        try:
            # Decode base64 to check validity
            photo_bytes = base64.b64decode(v)

            # Check file size
            max_size_bytes = cls.MAX_SIZE_MB * 1024 * 1024
            if len(photo_bytes) > max_size_bytes:
                raise ValueError(f"Photo size exceeds maximum of {cls.MAX_SIZE_MB}MB")

            # Validate image format
            validate_image_format(photo_bytes)

            return v
        except binascii.Error:
            raise ValueError("Invalid base64 encoding")
        except Exception as e:
            if "size" in str(e).lower():
                raise e
            raise ValueError(f"Photo validation failed: {str(e)}")


class TutorialGenerationRequest(BaseModel):
    """Request model for tutorial generation."""

    raw_description: str = Field(
        ...,
        max_length=5000,
        description="Raw description text for tutorial generation",
        alias="rawDescription",  # Accept camelCase from frontend
    )
    original_image_url: str = Field(
        ...,
        description="URL of the original/base image",
        alias="originalImageUrl",  # Accept camelCase from frontend
    )
    style_id: Optional[str] = Field(
        None,
        description="ID of the selected style (deprecated)",
        alias="styleId",  # Accept camelCase from frontend
    )
    customization_text: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional customization text for the tutorial",
        alias="customization",  # Accept camelCase from frontend
    )
    final_style_image_url: Optional[str] = Field(
        None,
        description="URL of the final style image",
        alias="finalStyleImageUrl",  # Accept camelCase from frontend
    )


class CustomizeStyleRequest(BaseModel):
    """Request model for style customization using two images."""

    original_image_url: str = Field(
        ...,
        description="URL of the original uploaded user photo",
        alias="originalImageUrl",  # Accept camelCase from frontend
    )
    style_image_url: str = Field(
        ...,
        description="URL of the selected style image",
        alias="styleImageUrl",  # Accept camelCase from frontend
    )
    custom_request: str = Field(
        ...,
        max_length=1000,
        description="Custom style request text from user",
        alias="customRequest",  # Accept camelCase from frontend
    )


# Alias for consistency with API naming
GenerateStylesRequest = PhotoUploadRequest
GenerateTutorialRequest = TutorialGenerationRequest


def validate_image_format(data: bytes) -> str:
    """
    Validate image format based on file signature.

    Args:
        data: Raw image bytes

    Returns:
        str: Image format (png, jpeg, webp)

    Raises:
        ValueError: If format is not supported
    """
    # Check PNG signature
    if data[:4] == b"\x89PNG":
        return "png"

    # Check JPEG signature
    if data[:3] == b"\xff\xd8\xff":
        return "jpeg"

    # Check WebP signature
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"

    raise ValueError("Unsupported image format. Only PNG, JPEG, and WebP are allowed.")


def validate_file_size(data: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate file size.

    Args:
        data: File data in bytes
        max_size_mb: Maximum allowed size in megabytes

    Returns:
        bool: True if size is valid

    Raises:
        ValueError: If file exceeds maximum size
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if len(data) > max_size_bytes:
        raise ValueError(f"File size exceeds maximum of {max_size_mb}MB")
    return True
