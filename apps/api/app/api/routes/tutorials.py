"""Tutorial generation endpoints."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from app.models.request import TutorialGenerationRequest
from app.models.response import ErrorResponse, TutorialResponse, TutorialStatusResponse
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
            raw_description=request.raw_description,
            original_image_url=request.original_image_url,
            style_id=request.style_id,
            customization_text=request.customization_text,
            final_style_image_url=request.final_style_image_url,
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


@router.get(
    "/{tutorial_id}",
    response_model=TutorialResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Tutorial not found"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve tutorial"},
    },
)
async def get_tutorial(tutorial_id: str) -> TutorialResponse:
    """
    Get a tutorial by ID.

    This endpoint retrieves the complete tutorial data with all steps,
    images, and videos for a previously generated tutorial.

    Args:
        tutorial_id: ID of the tutorial to retrieve

    Returns:
        TutorialResponse: Complete tutorial data with all steps

    Raises:
        HTTPException: If tutorial not found or retrieval fails
    """
    try:
        # Initialize service
        service = TutorialGenerationService()

        # Get tutorial
        tutorial = await service.get_tutorial(tutorial_id)

        return tutorial

    except ValueError as e:
        if "not found" in str(e).lower():
            logger.error(f"Tutorial not found: {tutorial_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "tutorial_not_found",
                    "message": f"Tutorial {tutorial_id} not found",
                },
            )
        else:
            logger.error(f"Tutorial retrieval failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "tutorial_retrieval_failed",
                    "message": str(e),
                },
            )
    except Exception as e:
        logger.error(f"Tutorial retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "tutorial_retrieval_failed",
                "message": f"Failed to retrieve tutorial: {str(e)}",
            },
        )


@router.get(
    "/{tutorial_id}/status",
    response_model=TutorialStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Tutorial not found"},
        500: {"model": ErrorResponse, "description": "Status check failed"},
    },
)
async def get_tutorial_status(tutorial_id: str) -> TutorialStatusResponse:
    """
    Get the status of a tutorial generation.

    This endpoint checks the progress of video generation for each step
    of the tutorial.

    Args:
        tutorial_id: ID of the tutorial to check

    Returns:
        TutorialStatusResponse: Current status and progress of the tutorial

    Raises:
        HTTPException: If tutorial not found or status check fails
    """
    try:
        # Initialize service
        service = TutorialGenerationService()

        # Check tutorial status
        status_response = await service.check_tutorial_status(tutorial_id)

        return status_response

    except ValueError as e:
        if "not found" in str(e).lower():
            logger.error(f"Tutorial not found: {tutorial_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "tutorial_not_found",
                    "message": f"Tutorial {tutorial_id} not found",
                },
            )
        else:
            logger.error(f"Status check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "status_check_failed",
                    "message": str(e),
                },
            )
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "status_check_failed",
                "message": f"Failed to check tutorial status: {str(e)}",
            },
        )
