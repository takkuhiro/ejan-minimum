"""Tutorial generation service."""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import List, Optional

import httpx
from PIL import Image


from app.models.response import (
    TutorialResponse,
    TutorialStep,
    TutorialStatusResponse,
    StepStatusInfo,
    StepStatus,
)
from app.services.ai_client import AIClient
from app.services.storage import StorageService
from app.services.tutorial_structure import TutorialStructureService
from app.services.image_generation import ImageGenerationService
from app.services.cloud_function_client import CloudFunctionClient
from app.core.config import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TutorialGenerationService:
    """Service for generating makeup tutorials with images and videos."""

    def __init__(self) -> None:
        """Initialize the tutorial generation service."""
        self.ai_client = AIClient()
        self.storage_service = StorageService()
        self.structure_service = TutorialStructureService(self.ai_client)
        self.image_service = ImageGenerationService(
            self.ai_client, self.storage_service
        )
        self.cloud_function_client = CloudFunctionClient()

    async def generate_tutorial(
        self,
        raw_description: str,
        original_image_url: str,
        style_id: Optional[str] = None,
        customization_text: Optional[str] = None,
    ) -> TutorialResponse:
        """
        Generate a complete tutorial from raw description.

        Args:
            raw_description: Raw text description for the tutorial
            original_image_url: URL of the original/base image
            style_id: Optional ID of the selected style (deprecated)
            customization_text: Optional customization text

        Returns:
            TutorialResponse with all steps, images, and videos
        """
        try:
            # Generate tutorial ID
            tutorial_id = f"tutorial_{uuid.uuid4().hex[:8]}"
            logger.info(f"Starting tutorial generation {tutorial_id}")

            # 1. Generate structured tutorial using Gemini
            logger.info("Generating tutorial structure from raw description")
            structured_tutorial = (
                await self.structure_service.generate_tutorial_structure(
                    style_description=raw_description,
                    custom_request=customization_text,
                )
            )

            # 2. Download original image
            original_image = await self._download_image(original_image_url)

            # 3. Save original image to GCS
            original_gcs_path = f"tutorials/{tutorial_id}/original.jpg"
            await self._save_image_to_gcs(original_image, original_gcs_path)

            # 4. Generate images and videos for each step
            steps = []
            previous_image = original_image
            previous_image_url = original_image_url
            bucket = self.storage_service.storage_client.get_bucket()

            for i, step_data in enumerate(structured_tutorial.steps):
                step_number = i + 1
                logger.info(f"Processing step {step_number}: {step_data.title}")

                # Generate completion image for this step
                completion_image = await self._generate_step_completion_image(
                    previous_image=previous_image,
                    step_title=step_data.title,
                    step_description=step_data.description,
                    step_number=step_number,
                )

                # Save completion image to GCS
                image_gcs_path = f"tutorials/{tutorial_id}/step_{step_number}/image.jpg"
                image_url = await self._save_image_to_gcs(
                    completion_image, image_gcs_path
                )

                # Prepare video path (video will be generated later)
                video_gcs_path = f"tutorials/{tutorial_id}/step_{step_number}/video.mp4"
                # Don't set video URL yet, as it doesn't exist
                video_public_url = None

                # Start video generation (async, will complete in background)
                # Use the previous step's image URL (or original for step 1)
                asyncio.create_task(
                    self._generate_step_video_async(
                        image_url=previous_image_url,
                        instruction_text=step_data.description,
                        target_gcs_path=video_gcs_path,
                        step_number=step_number,
                        tutorial_id=tutorial_id,
                    )
                )

                # Save step metadata
                step_metadata = {
                    "step_number": step_number,
                    "title": step_data.title,
                    "description": step_data.description,
                    "tools": step_data.tools_needed,
                    "created_at": datetime.now().isoformat(),
                }
                step_metadata_path = (
                    f"tutorials/{tutorial_id}/step_{step_number}/metadata.json"
                )
                step_metadata_blob = bucket.blob(step_metadata_path)
                step_metadata_blob.upload_from_string(
                    json.dumps(step_metadata, ensure_ascii=False),
                    content_type="application/json",
                )

                # Create tutorial step
                tutorial_step = TutorialStep(
                    step_number=step_number,
                    title=step_data.title,
                    description=step_data.description,
                    image_url=image_url,
                    video_url=video_public_url,  # URL where video will be available
                    tools=step_data.tools_needed,
                )
                steps.append(tutorial_step)

                # Update previous image and URL for next step
                previous_image = completion_image
                previous_image_url = image_url

            # 5. Save tutorial metadata
            await self._save_tutorial_metadata(
                tutorial_id=tutorial_id,
                title=structured_tutorial.title,
                description=structured_tutorial.description,
                total_steps=len(steps),
                original_image_url=original_image_url,
                raw_description=raw_description,
            )

            # 6. Create response
            tutorial = TutorialResponse(
                id=tutorial_id,
                title=structured_tutorial.title,
                description=structured_tutorial.description,
                total_steps=len(steps),
                steps=steps,
            )

            logger.info(f"Tutorial {tutorial_id} generation initiated successfully")
            return tutorial

        except Exception as e:
            logger.error(f"Failed to generate tutorial: {str(e)}")
            raise ValueError(f"Tutorial generation failed: {str(e)}")

    async def _download_image(self, image_url: str) -> Image.Image:
        """Download image from URL and return PIL Image."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                if response.status_code != 200:
                    raise ValueError(
                        f"Failed to download image: {response.status_code}"
                    )
                return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            raise ValueError(f"Failed to download image: {str(e)}")

    async def _save_image_to_gcs(self, image: Image.Image, gcs_path: str) -> str:
        """Save PIL Image to GCS and return public URL."""
        try:
            # Convert image to bytes
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=95)
            image_bytes = buffer.getvalue()

            # Upload to GCS
            bucket = self.storage_service.storage_client.get_bucket()
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(image_bytes, content_type="image/jpeg")
            blob.make_public()

            return str(blob.public_url)
        except Exception as e:
            logger.error(f"Failed to save image to GCS: {str(e)}")
            raise ValueError(f"Failed to save image to GCS: {str(e)}")

    async def _get_image_url(self, image: Image.Image, fallback_url: str) -> str:
        """Get URL for image, uploading if necessary."""
        try:
            # If we have the original URL, use it
            # For the first step, we use the original image URL
            # For subsequent steps, we need to use the saved GCS URLs
            return fallback_url
        except Exception:
            return fallback_url

    async def _generate_step_completion_image(
        self,
        previous_image: Image.Image,
        step_title: str,
        step_description: str,
        step_number: int,
    ) -> Image.Image:
        """Generate completion image for a step using previous image and description."""
        try:
            prompt = f"""Generate completed face image with these changes to the provided face image.
Step {step_number}: {step_title}
Instructions: {step_description}"""

            # Use image generation service with previous image
            response = self.ai_client.generate_content(
                model="gemini-2.5-flash-image-preview",
                prompt=prompt,
                image=previous_image,
            )

            # Extract generated image
            image_data = self.ai_client.extract_image_from_response(response)
            if not image_data:
                raise ValueError("No image generated")

            # Convert to PIL Image
            return Image.open(BytesIO(image_data))

        except Exception as e:
            logger.error(
                f"Failed to generate completion image for step {step_number}: {str(e)}"
            )
            # Fallback: return the previous image
            return previous_image

    async def _generate_step_video_async(
        self,
        image_url: str,
        instruction_text: str,
        target_gcs_path: str,
        step_number: int,
        tutorial_id: str,
    ) -> None:
        """Generate video for a step asynchronously."""
        try:
            logger.info(
                f"Starting video generation for tutorial {tutorial_id}, step {step_number}"
            )
            await self.cloud_function_client.generate_video(
                image_url=image_url,
                instruction_text=instruction_text,
                target_gcs_path=target_gcs_path,
                step_number=step_number,
            )
            logger.info(
                f"Video generation completed for tutorial {tutorial_id}, step {step_number}"
            )
        except Exception as e:
            logger.error(
                f"Video generation failed for tutorial {tutorial_id}, step {step_number}: {str(e)}"
            )

    async def _save_tutorial_metadata(
        self,
        tutorial_id: str,
        title: str,
        description: str,
        total_steps: int,
        original_image_url: str,
        raw_description: str,
    ) -> None:
        """Save tutorial metadata to GCS."""
        try:
            metadata = {
                "tutorial_id": tutorial_id,
                "title": title,
                "description": description,
                "total_steps": total_steps,
                "original_image_url": original_image_url,
                "raw_description": raw_description,
                "created_at": datetime.now().isoformat(),
                "status": "processing",
            }

            # Convert to JSON
            metadata_json = json.dumps(metadata, ensure_ascii=False, indent=2)

            # Save to GCS
            bucket = self.storage_service.storage_client.get_bucket()
            blob = bucket.blob(f"tutorials/{tutorial_id}/metadata.json")
            blob.upload_from_string(metadata_json, content_type="application/json")

            logger.info(f"Tutorial metadata saved for {tutorial_id}")
        except Exception as e:
            logger.error(f"Failed to save tutorial metadata: {str(e)}")

    async def get_tutorial(self, tutorial_id: str) -> TutorialResponse:
        """
        Get a tutorial by ID.

        Retrieves the complete tutorial data from Cloud Storage.

        Args:
            tutorial_id: ID of the tutorial to retrieve

        Returns:
            TutorialResponse with all steps and metadata

        Raises:
            ValueError: If tutorial not found or retrieval fails
        """
        try:
            # Load tutorial metadata
            bucket = self.storage_service.storage_client.get_bucket()
            metadata_blob = bucket.blob(f"tutorials/{tutorial_id}/metadata.json")

            if not metadata_blob.exists():
                raise ValueError(f"Tutorial {tutorial_id} not found")

            metadata_json = metadata_blob.download_as_text()
            metadata = json.loads(metadata_json)

            # Retrieve steps data
            total_steps = metadata.get("total_steps", 0)
            steps = []

            for step_num in range(1, total_steps + 1):
                # Construct step data from stored resources
                image_path = f"tutorials/{tutorial_id}/step_{step_num}/image.jpg"
                video_path = f"tutorials/{tutorial_id}/step_{step_num}/video.mp4"

                # Check if files exist and get public URLs
                image_blob = bucket.blob(image_path)
                video_blob = bucket.blob(video_path)

                image_url = None
                video_url = None

                if image_blob.exists():
                    image_url = f"https://storage.googleapis.com/{settings.storage_bucket}/{image_path}"

                if video_blob.exists():
                    video_url = f"https://storage.googleapis.com/{settings.storage_bucket}/{video_path}"

                # Try to load step metadata if available
                step_metadata_path = (
                    f"tutorials/{tutorial_id}/step_{step_num}/metadata.json"
                )
                step_metadata_blob = bucket.blob(step_metadata_path)

                if step_metadata_blob.exists():
                    step_metadata_json = step_metadata_blob.download_as_text()
                    step_data = json.loads(step_metadata_json)

                    step = TutorialStep(
                        step_number=step_num,
                        title=step_data.get("title", f"Step {step_num}"),
                        description=step_data.get("description", ""),
                        image_url=image_url,
                        video_url=video_url,
                        tools=step_data.get("tools", []),
                    )
                else:
                    # Fallback: create basic step data
                    step = TutorialStep(
                        step_number=step_num,
                        title=f"Step {step_num}",
                        description="",
                        image_url=image_url,
                        video_url=video_url,
                        tools=[],
                    )

                steps.append(step)

            # Create response
            tutorial = TutorialResponse(
                id=tutorial_id,
                title=metadata.get("title", "Tutorial"),
                description=metadata.get("description", ""),
                total_steps=total_steps,
                steps=steps,
            )

            logger.info(f"Tutorial {tutorial_id} retrieved successfully")
            return tutorial

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve tutorial: {str(e)}")
            raise ValueError(f"Failed to retrieve tutorial: {str(e)}")

    async def check_tutorial_status(self, tutorial_id: str) -> TutorialStatusResponse:
        """Check the status of a tutorial generation."""
        try:
            # Load tutorial metadata
            bucket = self.storage_service.storage_client.get_bucket()
            metadata_blob = bucket.blob(f"tutorials/{tutorial_id}/metadata.json")

            if not metadata_blob.exists():
                raise ValueError(f"Tutorial {tutorial_id} not found")

            metadata_json = metadata_blob.download_as_text()
            metadata = json.loads(metadata_json)

            # Check status of each step
            total_steps = metadata.get("total_steps", 0)
            steps_status = []
            completed_count = 0
            failed_count = 0

            for step_num in range(1, total_steps + 1):
                # First check step-specific status file
                step_status_path = (
                    f"tutorials/{tutorial_id}/step_{step_num}/status.json"
                )
                step_status_blob = bucket.blob(step_status_path)

                if step_status_blob.exists():
                    step_status_json = step_status_blob.download_as_text()
                    step_status_data = json.loads(step_status_json)

                    if step_status_data.get("status") == "completed":
                        status = StepStatus.COMPLETED
                        video_path = (
                            f"tutorials/{tutorial_id}/step_{step_num}/video.mp4"
                        )
                        video_url = f"https://storage.googleapis.com/{settings.storage_bucket}/{video_path}"
                        completed_count += 1
                    elif step_status_data.get("status") == "failed":
                        status = StepStatus.FAILED
                        video_url = None
                        failed_count += 1
                    else:
                        status = StepStatus.PROCESSING
                        video_url = None

                    error_message = step_status_data.get("error_message")
                else:
                    # Fallback: check if video file exists
                    video_path = f"tutorials/{tutorial_id}/step_{step_num}/video.mp4"
                    video_exists = self.storage_service.file_exists(video_path)

                    if video_exists:
                        status = StepStatus.COMPLETED
                        video_url = f"https://storage.googleapis.com/{settings.storage_bucket}/{video_path}"
                        completed_count += 1
                    else:
                        status = StepStatus.PENDING
                        video_url = None
                    error_message = None

                step_info = StepStatusInfo(
                    stepNumber=step_num,
                    status=status,
                    videoUrl=video_url,
                    errorMessage=error_message,
                )
                steps_status.append(step_info)

            # Calculate overall progress
            progress = (
                int((completed_count / total_steps * 100)) if total_steps > 0 else 0
            )

            # Determine overall status
            if completed_count == total_steps:
                overall_status = "completed"
            elif failed_count > 0 and completed_count > 0:
                overall_status = "partially_completed"
            elif failed_count == total_steps:
                overall_status = "failed"
            else:
                overall_status = "processing"

            return TutorialStatusResponse(
                tutorialId=tutorial_id,
                status=overall_status,
                progress=progress,
                steps=steps_status,
                createdAt=metadata.get("created_at", ""),
                updatedAt=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Failed to check tutorial status: {str(e)}")
            raise ValueError(f"Failed to check tutorial status: {str(e)}")

    async def _generate_sample_steps(
        self, style_id: str, customization_text: Optional[str] = None
    ) -> List[TutorialStep]:
        """
        Generate sample tutorial steps.

        In production, this would use the TutorialStructureService
        to generate structured steps from AI.
        """
        # Sample steps for demonstration
        base_url = "https://storage.googleapis.com/ejan-demo-storage"

        steps = [
            TutorialStep(
                step_number=1,
                title="スキンケアとベース準備",
                description="清潔な肌に保湿剤とプライマーを塗布します",
                image_url=f"{base_url}/tutorials/{style_id}/step1.png",
                video_url=f"{base_url}/tutorials/{style_id}/step1.mp4",
                tools=["保湿剤", "プライマー", "メイクスポンジ"],
            ),
            TutorialStep(
                step_number=2,
                title="ファンデーションの塗布",
                description="肌のトーンに合わせたファンデーションを均一に塗ります",
                image_url=f"{base_url}/tutorials/{style_id}/step2.png",
                video_url=f"{base_url}/tutorials/{style_id}/step2.mp4",
                tools=["ファンデーション", "ビューティーブレンダー", "コンシーラー"],
            ),
            TutorialStep(
                step_number=3,
                title="アイメイクの完成",
                description="アイシャドウ、アイライナー、マスカラを使用します",
                image_url=f"{base_url}/tutorials/{style_id}/step3.png",
                video_url=f"{base_url}/tutorials/{style_id}/step3.mp4",
                tools=[
                    "アイシャドウパレット",
                    "アイライナー",
                    "マスカラ",
                    "アイブラシ",
                ],
            ),
            TutorialStep(
                step_number=4,
                title="チークとハイライト",
                description="頬骨にチークを、鼻筋と頬骨の上にハイライトを入れます",
                image_url=f"{base_url}/tutorials/{style_id}/step4.png",
                video_url=f"{base_url}/tutorials/{style_id}/step4.mp4",
                tools=["チーク", "ハイライト", "ブラシ"],
            ),
            TutorialStep(
                step_number=5,
                title="リップメイクと仕上げ",
                description="リップライナーで輪郭を描き、リップスティックを塗ります",
                image_url=f"{base_url}/tutorials/{style_id}/step5.png",
                video_url=f"{base_url}/tutorials/{style_id}/step5.mp4",
                tools=["リップライナー", "リップスティック", "セッティングスプレー"],
            ),
        ]

        # Add customization influence if provided
        if customization_text and "eye" in customization_text.lower():
            # Emphasize eye makeup step
            steps[2].description += f" ({customization_text}を重視)"

        return steps

    async def generate_tutorial_with_real_services(
        self,
        style_id: str,
        style_image_url: str,
        customization_text: Optional[str] = None,
    ) -> TutorialResponse:
        """
        Generate a tutorial using real AI services.

        This is the production implementation that would use:
        - TutorialStructureService for structured content
        - ImageGenerationService for step images
        - Cloud Functions for video generation

        Args:
            style_id: ID of the selected style
            style_image_url: URL of the style image
            customization_text: Optional customization text

        Returns:
            TutorialResponse with AI-generated content
        """
        try:
            # 1. Generate structured tutorial using Gemini
            structured_tutorial = (
                await self.structure_service.generate_tutorial_structure(
                    style_description=f"Style {style_id}",
                    custom_request=customization_text,
                )
            )

            # 2. Generate step images using Nano Banana
            step_images = []
            for i, step in enumerate(structured_tutorial.steps):
                # Generate image for each step
                # This would use the image generation service
                image_url = await self._generate_step_image(
                    step.title, step.description
                )
                step_images.append(image_url)

            # 3. Generate videos using Cloud Functions (Veo3)
            step_videos = []
            for i, (step, image_url) in enumerate(
                zip(structured_tutorial.steps, step_images)
            ):
                # Call Cloud Function for video generation
                video_url = await self._generate_step_video(image_url, step.description)
                step_videos.append(video_url)

            # 4. Combine everything into TutorialResponse
            tutorial_id = f"tutorial_{uuid.uuid4().hex[:8]}"
            steps = []

            for i, step in enumerate(structured_tutorial.steps):
                tutorial_step = TutorialStep(
                    step_number=i + 1,
                    title=step.title,
                    description=step.description,
                    image_url=step_images[i],
                    video_url=step_videos[i],
                    tools=step.tools_needed,  # Use the correct attribute name
                )
                steps.append(tutorial_step)

            return TutorialResponse(
                id=tutorial_id,
                title=structured_tutorial.title,
                description=structured_tutorial.description,
                total_steps=len(steps),
                steps=steps,
            )

        except Exception as e:
            logger.error(f"Failed to generate tutorial with real services: {str(e)}")
            raise ValueError(f"Tutorial generation failed: {str(e)}")

    async def _generate_step_image(self, step_title: str, step_description: str) -> str:
        """
        Generate an image for a tutorial step.

        Args:
            step_title: Title of the step
            step_description: Description of the step

        Returns:
            URL of the generated image
        """
        # This would use the ImageGenerationService
        # For now, return a placeholder URL
        return f"https://storage.googleapis.com/ejan-demo-storage/generated/step_{uuid.uuid4().hex[:8]}.png"

    async def _generate_step_video(self, image_url: str, instruction: str) -> str:
        """
        Generate a video for a tutorial step using Cloud Function.

        Args:
            image_url: URL of the step image
            instruction: Instruction text for the video

        Returns:
            URL of the generated video
        """
        try:
            # Call Cloud Function for video generation
            video_url = await self.cloud_function_client.generate_video(
                image_url=image_url, instruction_text=instruction
            )
            return video_url
        except Exception as e:
            # Fallback to placeholder if Cloud Function is not available
            logger.warning(f"Cloud Function unavailable, using placeholder: {str(e)}")
            return f"https://storage.googleapis.com/ejan-demo-storage/generated/step_{uuid.uuid4().hex[:8]}.mp4"
