"""Style generation service for creating makeup styles."""

from typing import List
from io import BytesIO

from PIL import Image

from app.models.response import GeneratedStyle
from app.services.ai_client import AIClient
from app.services.storage import StorageService
from app.services.image_generation import ImageGenerationService, Gender


class StyleGenerationService:
    """Service for generating makeup styles using AI."""

    def __init__(self) -> None:
        """Initialize the style generation service."""
        self.ai_client = AIClient()
        self.storage_service = StorageService()
        self.image_service = ImageGenerationService(
            self.ai_client, self.storage_service
        )

    async def generate_styles(
        self, photo_bytes: bytes, gender: Gender, count: int = 3
    ) -> List[GeneratedStyle]:
        """
        Generate makeup styles for a user photo.

        Args:
            photo_bytes: User photo as bytes
            gender: Gender preference for style generation
            count: Number of styles to generate (default: 3)

        Returns:
            List of generated styles with images
        """
        # Create PIL Image object from bytes
        image = Image.open(BytesIO(photo_bytes))

        # Generate styles using the image generation service
        styles = await self.image_service.generate_three_styles(
            image=image, gender=gender
        )

        # Convert StyleGeneration objects to GeneratedStyle response models
        generated_styles = []
        for style in styles:
            generated_style = GeneratedStyle(
                id=style.id,
                title=style.title,
                description=style.description,
                imageUrl=style.image_url,  # Using alias
            )
            generated_styles.append(generated_style)

        return generated_styles
