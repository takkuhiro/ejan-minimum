"""
Unit tests for request/response data models.
Testing Pydantic models for API validation and serialization.
"""

import base64

import pytest
from pydantic import ValidationError


# Test for Gender enum
def test_gender_enum():
    """Test that Gender enum has expected values."""
    from app.models.request import Gender

    assert Gender.MALE.value == "male"
    assert Gender.FEMALE.value == "female"
    assert Gender.NEUTRAL.value == "neutral"


# Test for PhotoUploadRequest
class TestPhotoUploadRequest:
    """Test suite for PhotoUploadRequest model."""

    def test_valid_photo_upload_request(self):
        """Test creating a valid photo upload request."""
        from app.models.request import PhotoUploadRequest, Gender

        # Create valid base64 image data (small test PNG image)
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        test_image = b"\x89PNG\r\n\x1a\n" + b"test image data"
        base64_image = base64.b64encode(test_image).decode("utf-8")

        request = PhotoUploadRequest(photo=base64_image, gender=Gender.FEMALE)

        assert request.photo == base64_image
        assert request.gender == Gender.FEMALE

    def test_photo_size_validation(self):
        """Test that photo size is validated (max 10MB)."""
        from app.models.request import PhotoUploadRequest, Gender

        # Create image larger than 10MB
        large_image = b"x" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        base64_image = base64.b64encode(large_image).decode("utf-8")

        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo=base64_image, gender=Gender.MALE)

        errors = exc_info.value.errors()
        assert any("size" in str(error).lower() for error in errors)

    def test_invalid_base64(self):
        """Test that invalid base64 is rejected."""
        from app.models.request import PhotoUploadRequest, Gender

        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo="not valid base64!!!", gender=Gender.NEUTRAL)

        errors = exc_info.value.errors()
        assert any("base64" in str(error).lower() for error in errors)

    def test_missing_fields(self):
        """Test that required fields are validated."""
        from app.models.request import PhotoUploadRequest

        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 2  # photo and gender are required


# Test for TutorialGenerationRequest
class TestTutorialGenerationRequest:
    """Test suite for TutorialGenerationRequest model."""

    def test_valid_tutorial_request(self):
        """Test creating a valid tutorial generation request."""
        from app.models.request import TutorialGenerationRequest

        request = TutorialGenerationRequest(
            style_id="style-123", customization_text="Make it more natural"
        )

        assert request.style_id == "style-123"
        assert request.customization_text == "Make it more natural"

    def test_optional_customization(self):
        """Test that customization_text is optional."""
        from app.models.request import TutorialGenerationRequest

        request = TutorialGenerationRequest(style_id="style-456")

        assert request.style_id == "style-456"
        assert request.customization_text is None

    def test_customization_length_limit(self):
        """Test that customization text has a reasonable length limit."""
        from app.models.request import TutorialGenerationRequest

        # Test with very long customization text (over 1000 chars)
        long_text = "x" * 1001

        with pytest.raises(ValidationError) as exc_info:
            TutorialGenerationRequest(
                style_id="style-789", customization_text=long_text
            )

        errors = exc_info.value.errors()
        assert any(
            "length" in str(error).lower() or "1000" in str(error) for error in errors
        )


# Test for GeneratedStyle response
class TestGeneratedStyleResponse:
    """Test suite for GeneratedStyle response model."""

    def test_valid_generated_style(self):
        """Test creating a valid generated style response."""
        from app.models.response import GeneratedStyle

        style = GeneratedStyle(
            id="style-001",
            title="Natural Everyday Look",
            description="A fresh and clean makeup style perfect for daily wear",
            image_url="https://storage.googleapis.com/bucket/image.jpg",
        )

        assert style.id == "style-001"
        assert style.title == "Natural Everyday Look"
        assert (
            style.description == "A fresh and clean makeup style perfect for daily wear"
        )
        assert style.image_url == "https://storage.googleapis.com/bucket/image.jpg"

    def test_url_validation(self):
        """Test that image_url must be a valid URL."""
        from app.models.response import GeneratedStyle

        with pytest.raises(ValidationError) as exc_info:
            GeneratedStyle(
                id="style-002",
                title="Bold Evening Look",
                description="Dramatic makeup for special occasions",
                image_url="not a valid url",
            )

        errors = exc_info.value.errors()
        assert any("url" in str(error).lower() for error in errors)


# Test for StylesGenerationResponse
class TestGenerateStylesResponse:
    """Test suite for StylesGenerationResponse model."""

    def test_valid_styles_response(self):
        """Test creating a valid styles generation response."""
        from app.models.response import GenerateStylesResponse, GeneratedStyle

        styles = [
            GeneratedStyle(
                id="style-001",
                title="Natural Look",
                description="Daily wear makeup",
                image_url="https://example.com/image1.jpg",
            ),
            GeneratedStyle(
                id="style-002",
                title="Bold Look",
                description="Evening makeup",
                image_url="https://example.com/image2.jpg",
            ),
            GeneratedStyle(
                id="style-003",
                title="Professional Look",
                description="Office makeup",
                image_url="https://example.com/image3.jpg",
            ),
        ]

        response = GenerateStylesResponse(styles=styles)

        assert len(response.styles) == 3
        assert response.styles[0].title == "Natural Look"
        assert response.styles[1].title == "Bold Look"
        assert response.styles[2].title == "Professional Look"

    def test_empty_styles_list(self):
        """Test that empty styles list is invalid."""
        from app.models.response import GenerateStylesResponse

        with pytest.raises(ValidationError) as exc_info:
            GenerateStylesResponse(styles=[])

        errors = exc_info.value.errors()
        assert any(
            "empty" in str(error).lower() or "at least" in str(error).lower()
            for error in errors
        )


# Test for TutorialStep
class TestTutorialStep:
    """Test suite for TutorialStep model."""

    def test_valid_tutorial_step(self):
        """Test creating a valid tutorial step."""
        from app.models.response import TutorialStep

        step = TutorialStep(
            step_number=1,
            title="Apply Foundation",
            description="Apply foundation evenly across the face",
            image_url="https://example.com/step1-image.jpg",
            video_url="https://example.com/step1-video.mp4",
            tools=["Foundation brush", "Beauty sponge"],
        )

        assert step.step_number == 1
        assert step.title == "Apply Foundation"
        assert len(step.tools) == 2
        assert "Foundation brush" in step.tools

    def test_empty_tools_list(self):
        """Test that tools list can be empty."""
        from app.models.response import TutorialStep

        step = TutorialStep(
            step_number=2,
            title="Blend",
            description="Blend the foundation",
            image_url="https://example.com/step2-image.jpg",
            video_url="https://example.com/step2-video.mp4",
            tools=[],
        )

        assert step.tools == []

    def test_step_number_validation(self):
        """Test that step_number must be positive."""
        from app.models.response import TutorialStep

        with pytest.raises(ValidationError) as exc_info:
            TutorialStep(
                step_number=0,
                title="Invalid Step",
                description="This should fail",
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4",
                tools=[],
            )

        errors = exc_info.value.errors()
        assert any(
            "greater than 0" in str(error).lower() or "positive" in str(error).lower()
            for error in errors
        )


# Test for TutorialResponse
class TestTutorialResponse:
    """Test suite for TutorialResponse model."""

    def test_valid_tutorial_response(self):
        """Test creating a valid tutorial response."""
        from app.models.response import TutorialResponse, TutorialStep

        steps = [
            TutorialStep(
                step_number=1,
                title="Prep",
                description="Prepare the face",
                image_url="https://example.com/step1.jpg",
                video_url="https://example.com/step1.mp4",
                tools=["Cleanser"],
            ),
            TutorialStep(
                step_number=2,
                title="Apply",
                description="Apply makeup",
                image_url="https://example.com/step2.jpg",
                video_url="https://example.com/step2.mp4",
                tools=["Brush"],
            ),
        ]

        tutorial = TutorialResponse(
            id="tutorial-001",
            title="Natural Makeup Tutorial",
            description="Learn how to achieve a natural look",
            total_steps=2,
            steps=steps,
        )

        assert tutorial.id == "tutorial-001"
        assert tutorial.title == "Natural Makeup Tutorial"
        assert tutorial.total_steps == 2
        assert len(tutorial.steps) == 2

    def test_total_steps_mismatch(self):
        """Test that total_steps must match the length of steps list."""
        from app.models.response import TutorialResponse, TutorialStep

        steps = [
            TutorialStep(
                step_number=1,
                title="Step 1",
                description="First step",
                image_url="https://example.com/step1.jpg",
                video_url="https://example.com/step1.mp4",
                tools=[],
            )
        ]

        with pytest.raises(ValidationError) as exc_info:
            TutorialResponse(
                id="tutorial-002",
                title="Tutorial",
                description="Description",
                total_steps=5,  # Mismatch: only 1 step provided
                steps=steps,
            )

        errors = exc_info.value.errors()
        assert any("match" in str(error).lower() for error in errors)


# Test for ErrorResponse
class TestErrorResponse:
    """Test suite for ErrorResponse model."""

    def test_valid_error_response(self):
        """Test creating a valid error response."""
        from app.models.response import ErrorResponse

        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input provided",
            details={"field": "photo", "reason": "File size too large"},
        )

        assert error.error == "ValidationError"
        assert error.message == "Invalid input provided"
        assert error.details["field"] == "photo"

    def test_error_without_details(self):
        """Test that details field is optional."""
        from app.models.response import ErrorResponse

        error = ErrorResponse(
            error="ServerError", message="Internal server error occurred"
        )

        assert error.error == "ServerError"
        assert error.message == "Internal server error occurred"
        assert error.details is None

    def test_error_serialization(self):
        """Test that error response can be properly serialized to JSON."""
        from app.models.response import ErrorResponse

        error = ErrorResponse(
            error="NotFound",
            message="Style not found",
            details={"style_id": "invalid-id"},
        )

        json_data = error.model_dump()

        assert json_data["error"] == "NotFound"
        assert json_data["message"] == "Style not found"
        assert json_data["details"]["style_id"] == "invalid-id"


# Test for validation utilities
class TestValidationUtilities:
    """Test suite for validation utility functions."""

    def test_validate_image_format(self):
        """Test image format validation function."""
        from app.models.request import validate_image_format

        # Valid formats
        assert validate_image_format(b"\x89PNG") == "png"
        assert validate_image_format(b"\xff\xd8\xff") == "jpeg"
        assert validate_image_format(b"RIFF....WEBP") == "webp"

        # Invalid format
        with pytest.raises(ValueError) as exc_info:
            validate_image_format(b"INVALID")

        assert "unsupported" in str(exc_info.value).lower()

    def test_validate_file_size(self):
        """Test file size validation function."""
        from app.models.request import validate_file_size

        # Valid size (under 10MB)
        valid_data = b"x" * (5 * 1024 * 1024)  # 5MB
        assert validate_file_size(valid_data, max_size_mb=10) is True

        # Invalid size (over 10MB)
        invalid_data = b"x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(ValueError) as exc_info:
            validate_file_size(invalid_data, max_size_mb=10)

        assert "10MB" in str(exc_info.value)
