"""Tutorial generation service."""

import logging
import uuid
from typing import List, Optional


from app.models.response import TutorialResponse, TutorialStep
from app.services.ai_client import AIClient
from app.services.storage import StorageService
from app.services.tutorial_structure import TutorialStructureService
from app.services.image_generation import ImageGenerationService
from app.services.cloud_function_client import CloudFunctionClient


logger = logging.getLogger(__name__)


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
        self, style_id: str, customization_text: Optional[str] = None
    ) -> TutorialResponse:
        """
        Generate a complete tutorial for the selected style.

        Args:
            style_id: ID of the selected style
            customization_text: Optional customization text

        Returns:
            TutorialResponse with all steps, images, and videos
        """
        try:
            # For now, generate a sample tutorial
            # In production, this would:
            # 1. Retrieve style information from storage/cache
            # 2. Generate structured tutorial using Gemini
            # 3. Generate step images using Nano Banana
            # 4. Generate step videos using Veo3 (Cloud Function)

            # Generate tutorial ID
            tutorial_id = f"tutorial_{uuid.uuid4().hex[:8]}"

            # Create sample steps (in production, these would be generated)
            steps = await self._generate_sample_steps(style_id, customization_text)

            # Create tutorial response
            tutorial = TutorialResponse(
                id=tutorial_id,
                title="Professional Makeup Tutorial",
                description=f"Complete tutorial for style {style_id}"
                + (
                    f" with customization: {customization_text}"
                    if customization_text
                    else ""
                ),
                total_steps=len(steps),
                steps=steps,
            )

            logger.info(f"Generated tutorial {tutorial_id} for style {style_id}")
            return tutorial

        except Exception as e:
            logger.error(f"Failed to generate tutorial: {str(e)}")
            raise ValueError(f"Tutorial generation failed: {str(e)}")

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
