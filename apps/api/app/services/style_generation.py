"""Style generation service for creating makeup styles."""

from typing import List, Tuple, Optional
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
    ) -> Tuple[List[GeneratedStyle], Optional[str]]:
        """
        Generate makeup styles for a user photo.

        Args:
            photo_bytes: User photo as bytes
            gender: Gender preference for style generation
            count: Number of styles to generate (default: 3)

        Returns:
            Tuple of (List of generated styles with images, Original image URL)
        """
        # Create PIL Image object from bytes
        image = Image.open(BytesIO(photo_bytes))

        # Upload original image to storage
        original_image_url = None
        try:
            # Convert PIL Image to bytes for storage
            img_buffer = BytesIO()
            image.save(img_buffer, format="JPEG", quality=95)
            img_bytes = img_buffer.getvalue()

            # Upload to storage with correct content type
            original_image_url = self.storage_service.upload_image(
                data=img_bytes, content_type="image/jpeg"
            )
            print(f"Successfully uploaded original image to: {original_image_url}")
        except Exception as e:
            # Log error but continue with style generation
            print(f"Failed to upload original image: {e}")
            import traceback

            traceback.print_exc()

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
                rawDescription=style.raw_description,  # Using alias
                imageUrl=style.image_url,  # Using alias
            )
            generated_styles.append(generated_style)

        return generated_styles, original_image_url
