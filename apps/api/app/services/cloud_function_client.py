"""Cloud Function client for video generation."""

import asyncio
import logging
import os
import random
from typing import Optional, Dict, Any

import httpx
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class CloudFunctionClient:
    """Client for calling Cloud Functions."""

    def __init__(self) -> None:
        """Initialize Cloud Function client."""
        load_dotenv()
        self.function_url = os.getenv(
            "CLOUD_FUNCTION_URL",
            "https://us-central1-ejan-minimum.cloudfunctions.net/generate-video",
        )
        self.timeout = 600  # 10 minutes for video generation

    async def generate_video(
        self,
        image_url: str,
        instruction_text: str,
        target_gcs_path: Optional[str] = None,
        step_number: Optional[int] = None,
        max_retries: int = 5,
    ) -> str:
        """
        Call Cloud Function to generate a video with retry logic.

        Args:
            image_url: URL of the source image
            instruction_text: Text instruction for video generation
            target_gcs_path: Optional target path in GCS for the video
            step_number: Optional step number for tracking
            max_retries: Maximum number of retry attempts (default: 5)

        Returns:
            URL of the generated video

        Raises:
            ValueError: If video generation fails after all retries
            asyncio.TimeoutError: If generation times out
        """
        payload: Dict[str, Any] = {
            "image_url": image_url,
            "instruction_text": instruction_text,
            "prompt": instruction_text,  # Alias for compatibility
        }

        # Add optional parameters if provided
        if target_gcs_path:
            payload["target_gcs_path"] = target_gcs_path
        if step_number is not None:
            payload["step_number"] = step_number

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(
                        f"Calling Cloud Function for video generation "
                        f"(step {step_number}, attempt {attempt + 1}/{max_retries})"
                    )
                    response = await client.post(
                        self.function_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )

                    # Success case
                    if response.status_code == 200:
                        result = response.json()
                        video_url: str = result.get("video_url", "")

                        if video_url:
                            logger.info(f"Video generated successfully: {video_url}")
                            return video_url

                        # Check if Cloud Function itself failed due to rate limit
                        error = result.get("error", "")
                        if "rate limit" in error.lower() or "quota" in error.lower():
                            logger.warning(
                                f"Cloud Function reported rate limit (attempt {attempt + 1}/{max_retries})"
                            )
                            # Will continue to retry logic below
                        else:
                            raise ValueError("No video URL in Cloud Function response")

                    # Check if error is rate limit related (429 or 500 with rate limit message)
                    elif response.status_code == 429 or response.status_code == 500:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", "")
                            if (
                                "rate limit" in error_msg.lower()
                                or "quota" in error_msg.lower()
                                or response.status_code == 429
                            ):
                                # This is a rate limit error, we should retry
                                logger.warning(
                                    f"Rate limit error on attempt {attempt + 1}/{max_retries}: {error_msg}"
                                )
                            else:
                                # Non-rate-limit 500 error
                                error_msg = f"Cloud Function returned {response.status_code}: {response.text}"
                                logger.error(error_msg)
                                raise ValueError(error_msg)
                        except (ValueError, KeyError):
                            # If we can't parse the response, treat 429 as rate limit, 500 as error
                            if response.status_code == 429:
                                logger.warning(
                                    f"Rate limit error (429) on attempt {attempt + 1}/{max_retries}"
                                )
                            else:
                                error_msg = f"Cloud Function returned {response.status_code}: {response.text}"
                                logger.error(error_msg)
                                raise ValueError(error_msg)
                    else:
                        # Non-retryable error
                        error_msg = f"Cloud Function returned {response.status_code}: {response.text}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    # If we reach here, it's a rate limit error and we should retry
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        # Base wait: 10s, 20s, 40s, 80s, 160s (max ~2.7 minutes)
                        base_wait = min(10 * (2**attempt), 300)  # Cap at 5 minutes
                        jitter = random.uniform(
                            0, base_wait * 0.1
                        )  # Add up to 10% jitter
                        wait_time = base_wait + jitter

                        logger.info(
                            f"Retrying after {wait_time:.1f} seconds due to rate limit "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # Final attempt failed
                        logger.error(
                            f"Failed after {max_retries} retries due to rate limit"
                        )
                        raise ValueError(
                            f"Video generation failed after {max_retries} retries due to rate limit"
                        )

            except httpx.TimeoutException:
                logger.error(
                    f"Video generation timed out on attempt {attempt + 1}/{max_retries}"
                )
                if attempt < max_retries - 1:
                    # For timeout, use shorter wait time
                    wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s, 20s
                    logger.info(f"Retrying after {wait_time} seconds due to timeout")
                    await asyncio.sleep(wait_time)
                else:
                    raise asyncio.TimeoutError(
                        f"Video generation timed out after {max_retries} attempts"
                    )
            except ValueError:
                # Re-raise ValueError as-is (already logged)
                raise
            except Exception as e:
                # Unexpected errors are not retried
                logger.error(f"Unexpected error in video generation: {str(e)}")
                raise ValueError(f"Video generation failed: {str(e)}")

        # Should not reach here, but just in case
        raise ValueError(f"Video generation failed after {max_retries} attempts")

    async def check_function_health(self) -> bool:
        """
        Check if the Cloud Function is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(self.function_url)
                return response.status_code in [200, 405]  # 405 if GET not allowed
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
