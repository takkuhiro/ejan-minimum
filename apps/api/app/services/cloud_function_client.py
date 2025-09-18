"""Cloud Function client for video generation."""

import asyncio
import logging
import os

import httpx


logger = logging.getLogger(__name__)


class CloudFunctionClient:
    """Client for calling Cloud Functions."""

    def __init__(self) -> None:
        """Initialize Cloud Function client."""
        self.function_url = os.getenv(
            "CLOUD_FUNCTION_URL",
            "https://us-central1-ejan-minimum.cloudfunctions.net/generate-video",
        )
        self.timeout = 600  # 10 minutes for video generation

    async def generate_video(self, image_url: str, instruction_text: str) -> str:
        """
        Call Cloud Function to generate a video.

        Args:
            image_url: URL of the source image
            instruction_text: Text instruction for video generation

        Returns:
            URL of the generated video

        Raises:
            ValueError: If video generation fails
            asyncio.TimeoutError: If generation times out
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "image_url": image_url,
                    "instruction_text": instruction_text,
                }

                logger.info("Calling Cloud Function for video generation")
                response = await client.post(
                    self.function_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    error_msg = f"Cloud Function returned {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                result = response.json()
                video_url: str = result.get("video_url", "")

                if not video_url:
                    raise ValueError("No video URL in Cloud Function response")

                logger.info(f"Video generated successfully: {video_url}")
                return video_url

        except httpx.TimeoutException:
            logger.error("Video generation timed out")
            raise asyncio.TimeoutError("Video generation timed out after 10 minutes")
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise ValueError(f"Video generation failed: {str(e)}")

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
