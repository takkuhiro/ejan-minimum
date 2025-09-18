"""Unit tests for validation logic."""

import base64
import pytest
from pydantic import ValidationError

from app.models.request import (
    PhotoUploadRequest,
    TutorialGenerationRequest,
    Gender,
    validate_image_format,
    validate_file_size,
)


class TestGenderEnum:
    """Test Gender enumeration."""

    def test_gender_values(self) -> None:
        """Test all gender enum values are accessible."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.NEUTRAL.value == "neutral"

    def test_gender_from_string(self) -> None:
        """Test creating Gender from string values."""
        assert Gender("male") == Gender.MALE
        assert Gender("female") == Gender.FEMALE
        assert Gender("neutral") == Gender.NEUTRAL

    def test_gender_invalid_value(self) -> None:
        """Test invalid gender value raises error."""
        with pytest.raises(ValueError):
            Gender("invalid")


class TestImageFormatValidation:
    """Test image format validation function."""

    def test_validate_png_format(self) -> None:
        """Test PNG format detection."""
        png_header = b"\x89PNG\r\n\x1a\n" + b"rest of data"
        assert validate_image_format(png_header) == "png"

    def test_validate_jpeg_format(self) -> None:
        """Test JPEG format detection."""
        jpeg_header = b"\xff\xd8\xff\xe0" + b"rest of data"
        assert validate_image_format(jpeg_header) == "jpeg"

    def test_validate_webp_format(self) -> None:
        """Test WebP format detection."""
        webp_header = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"rest"
        assert validate_image_format(webp_header) == "webp"

    def test_validate_unsupported_format(self) -> None:
        """Test unsupported format raises error."""
        invalid_data = b"GIF89a"  # GIF header
        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_format(invalid_data)

    def test_validate_empty_data(self) -> None:
        """Test empty data raises error."""
        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_format(b"")

    def test_validate_short_data(self) -> None:
        """Test data too short for format detection."""
        with pytest.raises(ValueError, match="Unsupported image format"):
            validate_image_format(b"AB")


class TestFileSizeValidation:
    """Test file size validation function."""

    def test_validate_size_under_limit(self) -> None:
        """Test file size under limit passes."""
        data = b"x" * (5 * 1024 * 1024)  # 5MB
        assert validate_file_size(data, max_size_mb=10) is True

    def test_validate_size_at_limit(self) -> None:
        """Test file size exactly at limit passes."""
        data = b"x" * (10 * 1024 * 1024)  # 10MB
        assert validate_file_size(data, max_size_mb=10) is True

    def test_validate_size_over_limit(self) -> None:
        """Test file size over limit raises error."""
        data = b"x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(ValueError, match="File size exceeds maximum of 10MB"):
            validate_file_size(data, max_size_mb=10)

    def test_validate_custom_limit(self) -> None:
        """Test custom size limit."""
        data = b"x" * (3 * 1024 * 1024)  # 3MB
        assert validate_file_size(data, max_size_mb=5) is True

        with pytest.raises(ValueError, match="File size exceeds maximum of 2MB"):
            validate_file_size(data, max_size_mb=2)

    def test_validate_empty_file(self) -> None:
        """Test empty file passes validation."""
        assert validate_file_size(b"", max_size_mb=10) is True


class TestPhotoUploadRequest:
    """Test PhotoUploadRequest model validation."""

    @pytest.fixture
    def valid_photo_base64(self) -> str:
        """Create a valid base64 encoded PNG image."""
        # Small valid PNG image
        png_data = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90\x77\x53\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return base64.b64encode(png_data).decode("utf-8")

    @pytest.fixture
    def valid_jpeg_base64(self) -> str:
        """Create a valid base64 encoded JPEG image."""
        # Minimal JPEG structure
        jpeg_data = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xdb\x00\x43"
            + b"\x00" * 64  # Quantization table
            + b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"  # SOF
            b"\xff\xd9"  # EOI
        )
        return base64.b64encode(jpeg_data).decode("utf-8")

    @pytest.fixture
    def oversized_photo_base64(self) -> str:
        """Create an oversized base64 encoded image."""
        # Create 11MB of data with valid PNG header
        png_header = b"\x89PNG\r\n\x1a\n"
        large_data = png_header + b"x" * (11 * 1024 * 1024)
        return base64.b64encode(large_data).decode("utf-8")

    def test_valid_png_upload_request(self, valid_photo_base64: str) -> None:
        """Test valid PNG upload request."""
        request = PhotoUploadRequest(photo=valid_photo_base64, gender=Gender.FEMALE)
        assert request.photo == valid_photo_base64
        assert request.gender == Gender.FEMALE

    def test_valid_jpeg_upload_request(self, valid_jpeg_base64: str) -> None:
        """Test valid JPEG upload request."""
        request = PhotoUploadRequest(photo=valid_jpeg_base64, gender=Gender.MALE)
        assert request.photo == valid_jpeg_base64
        assert request.gender == Gender.MALE

    def test_all_gender_options(self, valid_photo_base64: str) -> None:
        """Test all gender options are valid."""
        for gender in [Gender.MALE, Gender.FEMALE, Gender.NEUTRAL]:
            request = PhotoUploadRequest(photo=valid_photo_base64, gender=gender)
            assert request.gender == gender

    def test_invalid_base64_encoding(self) -> None:
        """Test invalid base64 encoding raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo="not-valid-base64!@#", gender=Gender.FEMALE)
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("photo",)
        assert "Invalid base64 encoding" in errors[0]["msg"]

    def test_oversized_photo(self, oversized_photo_base64: str) -> None:
        """Test oversized photo raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo=oversized_photo_base64, gender=Gender.NEUTRAL)
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("photo",)
        assert "Photo size exceeds maximum of 10MB" in errors[0]["msg"]

    def test_unsupported_image_format(self) -> None:
        """Test unsupported image format raises error."""
        # GIF format (not supported)
        gif_data = b"GIF89a" + b"\x00" * 100
        gif_base64 = base64.b64encode(gif_data).decode("utf-8")

        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo=gif_base64, gender=Gender.MALE)
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("photo",)
        assert "Unsupported image format" in errors[0]["msg"]

    def test_missing_photo_field(self) -> None:
        """Test missing photo field raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(gender=Gender.FEMALE)  # type: ignore
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("photo",)
        assert errors[0]["type"] == "missing"

    def test_missing_gender_field(self, valid_photo_base64: str) -> None:
        """Test missing gender field raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(photo=valid_photo_base64)  # type: ignore
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("gender",)
        assert errors[0]["type"] == "missing"

    def test_invalid_gender_value(self, valid_photo_base64: str) -> None:
        """Test invalid gender value raises error."""
        with pytest.raises(ValidationError) as exc_info:
            PhotoUploadRequest(
                photo=valid_photo_base64, gender="invalid"  # type: ignore
            )
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("gender",)


class TestTutorialGenerationRequest:
    """Test TutorialGenerationRequest model validation."""

    def test_valid_request_minimal(self) -> None:
        """Test valid request with minimal fields."""
        request = TutorialGenerationRequest(style_id="style_123")
        assert request.style_id == "style_123"
        assert request.customization_text is None

    def test_valid_request_with_customization(self) -> None:
        """Test valid request with customization text."""
        custom_text = "Make it more dramatic with bold colors"
        request = TutorialGenerationRequest(
            style_id="style_456", customization_text=custom_text
        )
        assert request.style_id == "style_456"
        assert request.customization_text == custom_text

    def test_missing_style_id(self) -> None:
        """Test missing style_id raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TutorialGenerationRequest()  # type: ignore
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("style_id",)
        assert errors[0]["type"] == "missing"

    def test_empty_style_id(self) -> None:
        """Test empty style_id is allowed (though may not be business-valid)."""
        request = TutorialGenerationRequest(style_id="")
        assert request.style_id == ""

    def test_customization_text_max_length(self) -> None:
        """Test customization text max length validation."""
        # Exactly 1000 characters should pass
        max_text = "a" * 1000
        request = TutorialGenerationRequest(
            style_id="style_789", customization_text=max_text
        )
        assert request.customization_text == max_text

        # Over 1000 characters should fail
        long_text = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            TutorialGenerationRequest(
                style_id="style_789", customization_text=long_text
            )
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("customization_text",)
        assert "String should have at most 1000 characters" in errors[0]["msg"]

    def test_customization_text_empty_string(self) -> None:
        """Test empty customization text is treated as None-like."""
        request = TutorialGenerationRequest(style_id="style_999", customization_text="")
        assert request.style_id == "style_999"
        assert request.customization_text == ""

    def test_unicode_in_customization(self) -> None:
        """Test Unicode characters in customization text."""
        unicode_text = "メイクをもっとドラマチックに ✨💄"
        request = TutorialGenerationRequest(
            style_id="style_unicode", customization_text=unicode_text
        )
        assert request.customization_text == unicode_text

    def test_model_dict_export(self) -> None:
        """Test model exports correctly to dict."""
        request = TutorialGenerationRequest(
            style_id="test_id", customization_text="test text"
        )
        data = request.model_dump()
        assert data["style_id"] == "test_id"
        assert data["customization_text"] == "test text"

        # Test with None customization
        request_minimal = TutorialGenerationRequest(style_id="minimal")
        data_minimal = request_minimal.model_dump()
        assert data_minimal["style_id"] == "minimal"
        assert data_minimal["customization_text"] is None

    def test_model_json_export(self) -> None:
        """Test model exports correctly to JSON."""
        request = TutorialGenerationRequest(
            style_id="json_test", customization_text="json text"
        )
        json_str = request.model_dump_json()
        assert '"style_id":"json_test"' in json_str
        assert '"customization_text":"json text"' in json_str
