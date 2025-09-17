"""Style generation API endpoints."""

import base64
import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, status

from app.models.request import GenerateStylesRequest, Gender as RequestGender
from app.models.response import GenerateStylesResponse, GeneratedStyle
from app.services.style_generation import StyleGenerationService
from app.services.image_generation import Gender as ServiceGender

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/styles", tags=["styles"])

# Store generated styles in memory (for demo purposes)
# In production, this would be stored in a database
generated_styles_store: Dict[str, GeneratedStyle] = {}


@router.post(
    "/generate",
    response_model=GenerateStylesResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate makeup styles from user photo",
    description="Generates 3 makeup style suggestions based on user photo and gender preference",
)
async def generate_styles(request: GenerateStylesRequest) -> GenerateStylesResponse:
    """
    Generate makeup styles from user photo.

    Args:
        request: Request containing base64 encoded photo and gender

    Returns:
        Response with generated style suggestions

    Raises:
        HTTPException: If generation fails or validation errors occur
    """
    try:
        # Decode base64 photo
        try:
            photo_bytes = base64.b64decode(request.photo)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "INVALID_FORMAT",
                    "supportedFormats": ["JPEG", "PNG", "WebP"],
                    "message": "Invalid base64 encoding",
                },
            )

        # Check file size (10MB limit)
        max_size_bytes = 10 * 1024 * 1024
        if len(photo_bytes) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "FILE_TOO_LARGE",
                    "maxSize": max_size_bytes,
                    "currentSize": len(photo_bytes),
                    "message": "File size exceeds maximum of 10MB",
                },
            )

        # Validate image format
        if not _is_valid_image_format(photo_bytes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "type": "INVALID_FORMAT",
                    "supportedFormats": ["JPEG", "PNG", "WebP"],
                    "message": "Unsupported image format",
                },
            )

        # Convert Gender enum from request to service
        gender_map = {
            RequestGender.MALE: ServiceGender.MALE,
            RequestGender.FEMALE: ServiceGender.FEMALE,
            RequestGender.NEUTRAL: ServiceGender.NEUTRAL,
        }
        service_gender = gender_map[request.gender]

        # Generate styles using the service
        service = StyleGenerationService()
        styles = await service.generate_styles(
            photo_bytes=photo_bytes, gender=service_gender, count=3
        )

        # Store styles for later retrieval
        for style in styles:
            generated_styles_store[style.id] = style

        # Convert to response format
        response = GenerateStylesResponse(styles=styles)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate styles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.get(
    "/{style_id}",
    response_model=GeneratedStyle,
    summary="Get style details",
    description="Retrieve details of a previously generated style",
)
async def get_style(style_id: str) -> GeneratedStyle:
    """
    Get details of a specific style.

    Args:
        style_id: Unique identifier of the style

    Returns:
        Style details

    Raises:
        HTTPException: If style not found
    """
    if style_id not in generated_styles_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Style with ID '{style_id}' not found",
        )

    return generated_styles_store[style_id]


def _is_valid_image_format(data: bytes) -> bool:
    """
    Check if the image data is in a supported format.

    Args:
        data: Raw image bytes

    Returns:
        True if format is supported, False otherwise
    """
    # Check PNG signature
    if data[:4] == b"\x89PNG":
        return True

    # Check JPEG signature
    if data[:3] == b"\xff\xd8\xff":
        return True

    # Check WebP signature
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True

    return False
