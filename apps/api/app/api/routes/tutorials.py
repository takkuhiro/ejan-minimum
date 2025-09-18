"""Tutorial generation endpoints."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from app.models.request import TutorialGenerationRequest
from app.models.response import ErrorResponse, TutorialResponse
from app.services.tutorial_generation import TutorialGenerationService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tutorials", tags=["tutorials"])


@router.post(
    "/generate",
    response_model=TutorialResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Tutorial generation failed"},
        504: {"model": ErrorResponse, "description": "Tutorial generation timeout"},
    },
)
async def generate_tutorial(request: TutorialGenerationRequest) -> TutorialResponse:
    """
    Generate a tutorial for the selected style.

    This endpoint generates a complete tutorial with step-by-step instructions,
    images, and videos for achieving the selected makeup style.

    Args:
        request: Tutorial generation request with style ID and optional customization

    Returns:
        TutorialResponse: Generated tutorial with all steps

    Raises:
        HTTPException: If generation fails or times out
    """
    try:
        # Initialize service
        service = TutorialGenerationService()

        # Generate tutorial
        tutorial = await service.generate_tutorial(
            style_id=request.style_id,
            customization_text=request.customization_text,
        )

        return tutorial

    except asyncio.TimeoutError as e:
        logger.error(f"Tutorial generation timeout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": "timeout",
                "message": "Tutorial generation timed out. Please try again.",
            },
        )
    except NotImplementedError as e:
        # This is expected in RED phase
        logger.error(f"Tutorial generation not implemented: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "tutorial_generation_failed",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(f"Tutorial generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "tutorial_generation_failed",
                "message": f"Failed to generate tutorial: {str(e)}",
            },
        )
