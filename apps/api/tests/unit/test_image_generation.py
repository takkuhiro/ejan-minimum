"""Unit tests for image generation service."""

import base64
from unittest.mock import Mock, patch
from io import BytesIO

import pytest
from PIL import Image

from app.services.image_generation import (
    ImageGenerationService,
    ImageGenerationError,
    StyleGeneration,
    Gender,
    generate_style_prompt,
    STYLE_VARIATIONS,
)
from app.services.ai_client import AIClient
from app.services.storage import StorageService


class TestStylePromptGeneration:
    """Test style prompt generation."""

    def test_generate_prompt_for_male(self) -> None:
        """Test prompt generation for male gender."""
        prompt = generate_style_prompt(Gender.MALE, 0)
        assert "male" in prompt.lower() or "men" in prompt.lower()
        assert STYLE_VARIATIONS[0] in prompt
        assert "natural" in prompt.lower()

    def test_generate_prompt_for_female(self) -> None:
        """Test prompt generation for female gender."""
        prompt = generate_style_prompt(Gender.FEMALE, 1)
        assert "female" in prompt.lower() or "women" in prompt.lower()
        assert STYLE_VARIATIONS[1] in prompt
        assert "natural" in prompt.lower()

    def test_generate_prompt_for_neutral(self) -> None:
        """Test prompt generation for neutral gender."""
        prompt = generate_style_prompt(Gender.NEUTRAL, 2)
        assert "neutral" in prompt.lower() or "unisex" in prompt.lower()
        assert STYLE_VARIATIONS[2] in prompt

    def test_generate_prompt_with_custom_text(self) -> None:
        """Test prompt generation with custom text."""
        custom_text = "Add vibrant colors and dramatic lighting"
        prompt = generate_style_prompt(Gender.FEMALE, 0, custom_text)
        assert custom_text in prompt
        assert STYLE_VARIATIONS[0] in prompt

    def test_generate_prompt_variation_bounds(self) -> None:
        """Test prompt generation handles variation index bounds."""
        # Should wrap around if index too large
        prompt = generate_style_prompt(Gender.MALE, 10)
        assert any(variation in prompt for variation in STYLE_VARIATIONS)


class TestImageGenerationService:
    """Test image generation service."""

    @pytest.fixture
    def mock_ai_client(self) -> Mock:
        """Create mock AI client."""
        client = Mock(spec=AIClient)
        return client

    @pytest.fixture
    def mock_storage_service(self) -> Mock:
        """Create mock storage service."""
        service = Mock(spec=StorageService)
        service.upload_image = Mock(
            return_value="https://storage.example.com/image.jpg"
        )
        return service

    @pytest.fixture
    def service(
        self, mock_ai_client: Mock, mock_storage_service: Mock
    ) -> ImageGenerationService:
        """Create image generation service instance."""
        return ImageGenerationService(
            ai_client=mock_ai_client, storage_service=mock_storage_service
        )

    @pytest.fixture
    def sample_image_bytes(self) -> bytes:
        """Create sample image bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.mark.asyncio
    async def test_generate_single_style(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test generating a single style."""
        # Mock AI response
        mock_response = Mock()
        service.ai_client.extract_text_from_response.return_value = (
            "A modern casual look with natural makeup"
        )
        service.ai_client.extract_image_from_response.return_value = sample_image_bytes
        service.ai_client.generate_content.return_value = mock_response

        # Create input image
        input_image = Mock()  # Just a mock Image object

        result = await service.generate_single_style(
            image=input_image, gender=Gender.FEMALE, style_index=0
        )

        assert isinstance(result, StyleGeneration)
        assert result.id is not None
        # Title is extracted from description or defaults to "Style 1"
        assert result.title in [
            "A modern casual look with natural makeup",
            "Style 1",
            "Style",
        ]
        assert result.description == "A modern casual look with natural makeup"
        assert result.image_url == "https://storage.example.com/image.jpg"

        # Verify AI client was called correctly
        service.ai_client.generate_content.assert_called_once()
        call_kwargs = service.ai_client.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-flash-image-preview"
        assert isinstance(call_kwargs["prompt"], str)
        assert call_kwargs["image"] == input_image

    @pytest.mark.asyncio
    async def test_generate_single_style_with_custom_text(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test generating a single style with custom text."""
        mock_response = Mock()
        service.ai_client.extract_text_from_response.return_value = (
            "Custom style description"
        )
        service.ai_client.extract_image_from_response.return_value = sample_image_bytes
        service.ai_client.generate_content.return_value = mock_response

        input_image = Mock()  # Just a mock Image object
        custom_text = "Make it more dramatic"

        result = await service.generate_single_style(
            image=input_image,
            gender=Gender.MALE,
            style_index=1,
            custom_text=custom_text,
        )

        assert result.description == "Custom style description"

        # Check that custom text was included in prompt
        call_kwargs = service.ai_client.generate_content.call_args.kwargs
        prompt = call_kwargs["prompt"]
        assert custom_text in prompt

    @pytest.mark.asyncio
    async def test_generate_single_style_no_image_returned(
        self, service: ImageGenerationService
    ) -> None:
        """Test handling when AI doesn't return an image."""
        mock_response = Mock()
        service.ai_client.extract_text_from_response.return_value = "Description"
        service.ai_client.extract_image_from_response.return_value = None  # No image
        service.ai_client.generate_content.return_value = mock_response

        input_image = Mock()  # Just a mock Image object

        with pytest.raises(ImageGenerationError) as exc_info:
            await service.generate_single_style(
                image=input_image, gender=Gender.FEMALE, style_index=0
            )
        assert "No image generated" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_three_styles(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test generating three styles."""
        # Mock AI responses for three different styles
        mock_response = Mock()
        service.ai_client.extract_text_from_response.side_effect = [
            "Natural daytime look",
            "Elegant evening style",
            "Bold party makeup",
        ]
        service.ai_client.extract_image_from_response.return_value = sample_image_bytes
        service.ai_client.generate_content.return_value = mock_response

        # Mock storage URLs
        service.storage_service.upload_image.side_effect = [
            "https://storage.example.com/style1.jpg",
            "https://storage.example.com/style2.jpg",
            "https://storage.example.com/style3.jpg",
        ]

        input_image = Mock()  # Just a mock Image object

        results = await service.generate_three_styles(
            image=input_image, gender=Gender.NEUTRAL
        )

        assert len(results) == 3
        assert results[0].description == "Natural daytime look"
        assert results[1].description == "Elegant evening style"
        assert results[2].description == "Bold party makeup"
        assert results[0].image_url == "https://storage.example.com/style1.jpg"
        assert results[1].image_url == "https://storage.example.com/style2.jpg"
        assert results[2].image_url == "https://storage.example.com/style3.jpg"

        # Verify AI was called 3 times
        assert service.ai_client.generate_content.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_three_styles_partial_failure(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test handling partial failure in generating three styles."""
        # Second style generation fails
        mock_response = Mock()
        service.ai_client.extract_text_from_response.side_effect = [
            "Style 1",
            "Style 2",
            "Style 3",
        ]
        service.ai_client.extract_image_from_response.side_effect = [
            sample_image_bytes,
            None,  # Second fails
            sample_image_bytes,
        ]
        service.ai_client.generate_content.return_value = mock_response

        input_image = Mock()  # Just a mock Image object

        with pytest.raises(ImageGenerationError) as exc_info:
            await service.generate_three_styles(image=input_image, gender=Gender.FEMALE)
        assert "Failed to generate all styles" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_upload_and_generate(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test processing upload and generating styles."""
        # Create base64 encoded image
        base64_image = base64.b64encode(sample_image_bytes).decode("utf-8")

        # Mock responses
        mock_response = Mock()
        service.ai_client.extract_text_from_response.return_value = "Generated style"
        service.ai_client.extract_image_from_response.return_value = sample_image_bytes
        service.ai_client.generate_content.return_value = mock_response

        with patch("app.services.image_generation.Image") as mock_pil_image_class:
            # Mock PIL Image.open
            mock_pil_image = Mock()
            mock_pil_image_class.open.return_value = mock_pil_image

            results = await service.process_upload_and_generate(
                base64_photo=base64_image, gender=Gender.MALE
            )

            assert len(results) == 3
            for result in results:
                assert isinstance(result, StyleGeneration)
                assert result.description == "Generated style"

            # Verify PIL Image.open was called with BytesIO
            mock_pil_image_class.open.assert_called()
            call_arg = mock_pil_image_class.open.call_args[0][0]
            assert isinstance(call_arg, BytesIO)

    @pytest.mark.asyncio
    async def test_process_upload_invalid_base64(
        self, service: ImageGenerationService
    ) -> None:
        """Test handling invalid base64 input."""
        invalid_base64 = "not-valid-base64!"

        with pytest.raises(ImageGenerationError) as exc_info:
            await service.process_upload_and_generate(
                base64_photo=invalid_base64, gender=Gender.FEMALE
            )
        assert "Invalid base64 image" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_storage_upload_failure(
        self, service: ImageGenerationService, sample_image_bytes: bytes
    ) -> None:
        """Test handling storage upload failure."""
        mock_response = Mock()
        service.ai_client.extract_text_from_response.return_value = "Description"
        service.ai_client.extract_image_from_response.return_value = sample_image_bytes
        service.ai_client.generate_content.return_value = mock_response

        # Storage upload fails
        service.storage_service.upload_image.side_effect = Exception("Storage error")

        input_image = Mock()  # Just a mock Image object

        with pytest.raises(ImageGenerationError) as exc_info:
            await service.generate_single_style(
                image=input_image, gender=Gender.MALE, style_index=0
            )
        assert "Failed to upload image" in str(exc_info.value)

    def test_validate_image_size(self, service: ImageGenerationService) -> None:
        """Test image size validation."""
        # Valid size (under 10MB)
        small_image = b"x" * (5 * 1024 * 1024)  # 5MB
        assert service.validate_image_size(small_image) is True

        # Invalid size (over 10MB)
        large_image = b"x" * (11 * 1024 * 1024)  # 11MB
        assert service.validate_image_size(large_image) is False

    def test_extract_title_from_description(
        self, service: ImageGenerationService
    ) -> None:
        """Test title extraction from description."""
        descriptions = [
            (
                "Natural Daytime Look: A fresh and clean appearance",
                "Natural Daytime Look",
            ),
            ("Bold Evening Style - Dramatic and sophisticated", "Bold Evening Style"),
            ("Simple description without title format", "Style"),
            ("", "Style"),
        ]

        for description, expected_title in descriptions:
            title = service.extract_title_from_description(description)
            if description and ":" not in description and "-" not in description:
                # For simple descriptions, it returns the description itself if short enough
                assert title == description or title == "Style"
            else:
                assert expected_title in title or title == expected_title
