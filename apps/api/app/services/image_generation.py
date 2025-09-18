"""Image generation service using Nano Banana (Gemini 2.5 Flash Image Preview)."""

import base64
import uuid
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from io import BytesIO
import time

from PIL import Image
from pydantic import BaseModel, Field

from app.services.ai_client import AIClient, AIClientAPIError
from app.services.storage import StorageService


class Gender(str, Enum):
    """Gender options for style generation."""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class ImageGenerationError(Exception):
    """Exception raised during image generation."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        """Initialize with message and optional underlying cause."""
        super().__init__(message)
        if cause:
            self.__cause__ = cause


@dataclass
class StyleGeneration:
    """Represents a generated style with image."""

    id: str
    title: str
    description: str
    raw_description: str
    image_url: str


class JapaneseStyleInfo(BaseModel):
    """Model for Japanese style information."""

    title: str = Field(description="日本語のタイトル（10文字以内）")
    description: str = Field(description="日本語の説明文（30文字以内）")


STYLE_VARIATIONS = {
    "male0": "Fresh and Natural Style Hair: A neat, short haircut in a natural color. The front is kept down slightly to create a light, effortless feel. Use minimal wax to maintain the hair's natural flow. Makeup: Focus on grooming. Tidy the eyebrows and use lip balm to prevent dryness. Avoid foundation and keep the skin tone even for a healthy appearance.",
    "male1": "Sophisticated and Conservative Style Hair: Dark, short hair with a sleek side part or slicked-back style. A glossy finish adds a polished, intelligent impression. Makeup: Fill in sparse areas of the eyebrows for a defined shape. Use a translucent powder to control shine and maintain a clean look.",
    "male2": "Soft and Casual Style Hair: A light mushroom cut or a slightly longer wolf cut. Ash or beige hair colors will soften the overall look. Makeup: Use an eyebrow pencil to match the hair color and a light BB cream to even out the skin. A tinted lip balm adds a healthy flush of color.",
    "female0": "Elegant and Feminine Style Hair: A sleek, glossy long hairstyle or a soft, inward-curling bob. The bangs can be swept to the side or kept as a see-through fringe for a lighter feel. Makeup: A dewy, translucent base. Use soft, skin-tone eyeshadows like beige or pale pink. A glossy finish on the lips gives a natural, fresh look.",
    "feamle1": "Cool and Professional Style Hair: A sharp chin-length bob or a medium-length style with swept-back bangs. Dark hair colors create a sophisticated and composed impression. Makeup: A matte foundation. A sharp winged eyeliner adds a cool edge, while nude or deep-colored lipstick enhances the mature, elegant vibe.",
    "female2": "Cute and Doll-like Style Hair: A cute outward or inward-curling bob with straight-across bangs. Adding highlights can create a fun, dimensional look. Makeup: Use glittery eyeshadows and highlight the undereye bags (aegyo sal) for a sparkling effect. Pink or coral blush on the apples of the cheeks and a cute-colored lipstick complete the youthful look.",
    "neutral0": "Natural and Androgynous Style Hair: A versatile mushroom short cut or a short style that exposes the ears. Dark hair colors contribute to a cool and neutral look. Makeup: Focus on skin prep and grooming. Use moisturizers on dry areas to create a healthy glow, and simply groom the eyebrows for a clean finish.",
    "neutral1": "Cool and Edgy Style Hair: A wet-look short cut or a two-block undercut with shaved sides. These styles are distinct yet cohesive. Makeup: A matte base and a sharp contour to define the face. A slightly winged eyeliner and a matte lip color that subdues natural tones will enhance a sleek, modern look.",
    "neutral2": "Soft and Feminine Style Hair: A soft perm or a slightly longer wolf cut. Lighter hair colors create a gentle and relaxed atmosphere. Makeup: A dewy foundation with soft, sheer eyeshadows and blush in pink or orange tones. A glossy lip adds a touch of femininity and warmth.",
}


def generate_style_prompt(
    gender: Gender, style_index: int, custom_text: Optional[str] = None
) -> str:
    """Generate prompt for style creation.

    Args:
        gender: Gender for style generation.
        style_index: Index of style variation (0-2).
        custom_text: Optional custom request text.

    Returns:
        Generated prompt string.
    """
    # Ensure style_index is within bounds
    key = f"{gender.value}{style_index}"
    style_variation = STYLE_VARIATIONS[key]

    # Gender-specific language
    gender_text = {
        Gender.MALE: "male/men's",
        Gender.FEMALE: "female/women's",
        Gender.NEUTRAL: "gender-neutral/unisex",
    }[gender]

    base_prompt = f"""Generate a realistic image of the given face photo with a perfect {gender_text} hairstyle and makeup style.
STYLE: {style_variation}
Please make the style natural and in line with current trends. Avoid anything too bizarre or extreme.
Keep the facial features and identity unchanged, only modify the hairstyle and makeup.
Provide a brief description of the style and steps to achieve this look and you must generate the image."""

    if custom_text:
        base_prompt += f"\n\nAdditional request: {custom_text}"

    return base_prompt


class ImageGenerationService:
    """Service for generating styled images using Nano Banana."""

    def __init__(self, ai_client: AIClient, storage_service: StorageService):
        """Initialize image generation service.

        Args:
            ai_client: AI client for Gemini API.
            storage_service: Storage service for uploading images.
        """
        self.ai_client = ai_client
        self.storage_service = storage_service
        self.model_name = "gemini-2.5-flash-image-preview"
        self.sub_model_name = "gemini-2.0-flash-lite"

    async def generate_single_style(
        self,
        image: Image.Image,
        gender: Gender,
        style_index: int,
        custom_text: Optional[str] = None,
    ) -> StyleGeneration:
        """Generate a single style for the given image.

        Args:
            image: Input face PIL Image.
            gender: Gender for style generation.
            style_index: Index of style variation (0-2).
            custom_text: Optional custom request text.

        Returns:
            Generated style with image URL.

        Raises:
            ImageGenerationError: If generation fails.
        """
        max_retries = 3
        retry_count = 0
        base_sleep_time = 2  # Base sleep time in seconds

        while retry_count < max_retries:
            try:
                # Generate prompt
                prompt = generate_style_prompt(gender, style_index, custom_text)

                # Call AI API
                response = self.ai_client.generate_content(
                    model=self.model_name,
                    prompt=prompt,
                    image=image,
                )

                # Extract raw description from main model
                raw_description = self.ai_client.extract_text_from_response(response)
                print(f"raw_description: {raw_description}")
                if not raw_description:
                    raw_description = f"Style {style_index + 1} for {gender.value}"

                # Generate Japanese title and description using sub model
                try:
                    japanese_response = self.ai_client.client.models.generate_content(
                        model=self.sub_model_name,
                        contents=f"""以下の英語のスタイル説明を日本語に翻訳し、魅力的なタイトル（10文字以内）と説明文（30文字以内）を生成してください。
                        タイトルはキャッチーで覚えやすいものにしてください。
                        説明文は簡潔でわかりやすくしてください。

                        英語の説明:
                        {raw_description}""",
                        config={
                            "response_mime_type": "application/json",
                            "response_schema": JapaneseStyleInfo,
                        },
                    )
                    japanese_info: JapaneseStyleInfo = japanese_response.parsed
                    title = japanese_info.title
                    description = japanese_info.description
                    print(f"Japanese title: {title}, description: {description}")
                except Exception as e:
                    print(f"Failed to generate Japanese text: {e}")
                    # Fallback to extracting from raw description
                    title = (
                        self.extract_title_from_description(raw_description)
                        or f"スタイル{style_index + 1}"
                    )
                    description = (
                        raw_description[:30]
                        if raw_description
                        else f"{gender.value}スタイル"
                    )

                # Extract generated image
                image_data = self.ai_client.extract_image_from_response(response)
                if not image_data:
                    retry_count += 1
                    if retry_count < max_retries:
                        # Calculate exponential backoff with max limit
                        sleep_time = min(base_sleep_time * (2 ** (retry_count - 1)), 20)
                        print(
                            f"No image generated, retrying in {sleep_time}s... (attempt {retry_count}/{max_retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise ImageGenerationError(
                            f"No image generated after {max_retries} attempts"
                        )

                # Upload to storage
                try:
                    # Determine content type
                    content_type = "image/png"
                    image_url = self.storage_service.upload_image(
                        image_data, content_type
                    )
                except Exception as e:
                    raise ImageGenerationError(f"Failed to upload image: {e}")

                # Create style object
                style_id = str(uuid.uuid4())

                return StyleGeneration(
                    id=style_id,
                    title=title,
                    description=description,
                    raw_description=raw_description,
                    image_url=image_url,
                )

            except AIClientAPIError as e:
                # Handle 500 errors with retry
                if "500" in str(e) or "INTERNAL" in str(e):
                    retry_count += 1
                    if retry_count < max_retries:
                        # Calculate exponential backoff with max limit
                        sleep_time = min(base_sleep_time * (2**retry_count), 20)
                        print(
                            f"AI API returned 500 error, retrying in {sleep_time}s... (attempt {retry_count}/{max_retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                raise ImageGenerationError(f"AI generation failed: {e}")
            except ImageGenerationError:
                raise  # Re-raise our own errors
            except Exception as e:
                raise ImageGenerationError(f"Unexpected error: {e}")

        # Should never reach here, but for type safety
        raise ImageGenerationError("Failed to generate style after all retries")

    async def generate_three_styles(
        self, image: Image.Image, gender: Gender, custom_text: Optional[str] = None
    ) -> List[StyleGeneration]:
        """Generate three different styles for the given image.

        Args:
            image: Input face PIL Image.
            gender: Gender for style generation.
            custom_text: Optional custom request text.

        Returns:
            List of generated styles (at least one).

        Raises:
            ImageGenerationError: If all generation attempts fail.
        """
        styles = []
        errors = []

        for i in range(3):
            try:
                style = await self.generate_single_style(
                    image=image, gender=gender, style_index=i, custom_text=custom_text
                )
                styles.append(style)
            except ImageGenerationError as e:
                errors.append(f"Style {i+1}: {e}")
                print(f"Failed to generate style {i+1}: {e}")

            # Add delay between API calls to avoid rate limiting
            if i < 2:  # Don't sleep after last iteration
                time.sleep(2)  # Increased delay

        # Return partial results if we have at least one successful generation
        if len(styles) > 0:
            if len(styles) < 3:
                print(f"Generated {len(styles)}/3 styles. Errors: {', '.join(errors)}")
            return styles

        # Only raise error if all attempts failed
        error_msg = "Failed to generate any styles. " + " ".join(errors)
        raise ImageGenerationError(error_msg)

    async def process_upload_and_generate(
        self, base64_photo: str, gender: Gender, custom_text: Optional[str] = None
    ) -> List[StyleGeneration]:
        """Process uploaded photo and generate styles.

        Args:
            base64_photo: Base64 encoded photo.
            gender: Gender for style generation.
            custom_text: Optional custom request text.

        Returns:
            List of generated styles.

        Raises:
            ImageGenerationError: If processing fails.
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_photo)
        except Exception as e:
            raise ImageGenerationError(f"Invalid base64 image: {e}")

        # Validate size (10MB limit)
        if not self.validate_image_size(image_data):
            raise ImageGenerationError("Image size exceeds 10MB limit")

        # Create PIL Image object from bytes
        try:
            image = Image.open(BytesIO(image_data))
        except Exception as e:
            raise ImageGenerationError(f"Failed to open image: {e}")

        # Generate styles
        return await self.generate_three_styles(image, gender, custom_text)

    def validate_image_size(self, image_data: bytes, max_size_mb: int = 10) -> bool:
        """Validate image size is within limit.

        Args:
            image_data: Image bytes.
            max_size_mb: Maximum size in MB.

        Returns:
            True if size is valid, False otherwise.
        """
        size_mb = len(image_data) / (1024 * 1024)
        return size_mb <= max_size_mb

    def extract_title_from_description(self, description: str) -> str:
        """Extract title from description text.

        Args:
            description: Full description text.

        Returns:
            Extracted title or default.
        """
        if not description:
            return "Style"

        # Try to extract first line or sentence as title
        lines = description.strip().split("\n")
        if lines:
            # Check for common title patterns
            first_line = lines[0].strip()
            if ":" in first_line:
                return first_line.split(":")[0].strip()
            elif "-" in first_line:
                return first_line.split("-")[0].strip()
            elif len(first_line) < 50:  # Short enough to be a title
                return first_line

        return "Style"
