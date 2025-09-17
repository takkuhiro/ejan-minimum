"""Unit tests for AI client service."""

import os
from unittest.mock import Mock, patch

import pytest
from google import genai
from google.genai import types

from app.services.ai_client import (
    AIClient,
    AIClientInitError,
    AIClientAPIError,
)


class TestAIClientInitialization:
    """Test AI client initialization."""

    def test_init_with_valid_api_key(self) -> None:
        """Test initialization with valid API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"}):
            client = AIClient()
            assert client.api_key == "test-api-key"
            assert client.client is not None
            assert isinstance(client.client, genai.Client)

    def test_init_without_api_key(self) -> None:
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AIClientInitError) as exc_info:
                AIClient()
            assert "GOOGLE_API_KEY is not set" in str(exc_info.value)

    def test_init_with_custom_api_key(self) -> None:
        """Test initialization with custom API key."""
        client = AIClient(api_key="custom-key")
        assert client.api_key == "custom-key"
        assert client.client is not None

    @patch("app.services.ai_client.genai.Client")
    def test_client_creation_failure(self, mock_client_class: Mock) -> None:
        """Test handling of client creation failure."""
        mock_client_class.side_effect = Exception("Failed to create client")

        with pytest.raises(AIClientInitError) as exc_info:
            AIClient(api_key="test-key")
        assert "Failed to initialize AI client" in str(exc_info.value)


class TestAIClientMethods:
    """Test AI client methods."""

    @pytest.fixture
    def ai_client(self) -> AIClient:
        """Create AI client instance for testing."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            client = AIClient()
            client.client = Mock(spec=genai.Client)
            return client

    def test_generate_content_success(self, ai_client: AIClient) -> None:
        """Test successful content generation."""
        # Mock the response structure
        mock_response = Mock()
        mock_response.candidates = [
            Mock(content=Mock(parts=[Mock(text="Generated text", inline_data=None)]))
        ]

        ai_client.client.models.generate_content.return_value = mock_response

        result = ai_client.generate_content(
            model="gemini-2.5-flash", prompt="Test prompt"
        )

        assert result == mock_response
        ai_client.client.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash", contents=["Test prompt"]
        )

    def test_generate_content_with_image(self, ai_client: AIClient) -> None:
        """Test content generation with image."""
        mock_image = Mock(spec=types.Image)
        mock_response = Mock()
        mock_response.candidates = [
            Mock(content=Mock(parts=[Mock(text="Generated text", inline_data=None)]))
        ]

        ai_client.client.models.generate_content.return_value = mock_response

        result = ai_client.generate_content(
            model="gemini-2.5-flash-image-preview",
            prompt="Test prompt",
            image=mock_image,
        )

        assert result == mock_response
        ai_client.client.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash-image-preview", contents=["Test prompt", mock_image]
        )

    def test_generate_content_api_error(self, ai_client: AIClient) -> None:
        """Test API error handling in content generation."""
        ai_client.client.models.generate_content.side_effect = Exception("API Error")

        with pytest.raises(AIClientAPIError) as exc_info:
            ai_client.generate_content(model="gemini-2.5-flash", prompt="Test prompt")
        assert "API Error" in str(exc_info.value)

    def test_generate_content_with_retry(self, ai_client: AIClient) -> None:
        """Test content generation with retry logic."""
        mock_response = Mock()
        mock_response.candidates = [
            Mock(
                content=Mock(parts=[Mock(text="Success after retry", inline_data=None)])
            )
        ]

        # First two calls fail, third succeeds
        ai_client.client.models.generate_content.side_effect = [
            Exception("Temporary failure"),
            Exception("Another temporary failure"),
            mock_response,
        ]

        result = ai_client.generate_content_with_retry(
            model="gemini-2.5-flash", prompt="Test prompt", max_retries=3
        )

        assert result == mock_response
        assert ai_client.client.models.generate_content.call_count == 3

    def test_generate_content_with_retry_exhausted(self, ai_client: AIClient) -> None:
        """Test retry exhaustion in content generation."""
        ai_client.client.models.generate_content.side_effect = Exception(
            "Persistent failure"
        )

        with pytest.raises(AIClientAPIError) as exc_info:
            ai_client.generate_content_with_retry(
                model="gemini-2.5-flash", prompt="Test prompt", max_retries=3
            )

        assert "Failed after 3 retries" in str(exc_info.value)
        assert ai_client.client.models.generate_content.call_count == 3

    def test_extract_text_from_response(self, ai_client: AIClient) -> None:
        """Test text extraction from response."""
        mock_response = Mock()
        mock_response.candidates = [
            Mock(
                content=Mock(
                    parts=[
                        Mock(text="First text", inline_data=None),
                        Mock(text=None, inline_data=Mock(data=b"image_data")),
                        Mock(text="Second text", inline_data=None),
                    ]
                )
            )
        ]

        text = ai_client.extract_text_from_response(mock_response)
        assert text == "First text\nSecond text"

    def test_extract_image_from_response(self, ai_client: AIClient) -> None:
        """Test image extraction from response."""
        image_data = b"test_image_data"
        mock_response = Mock()
        mock_response.candidates = [
            Mock(
                content=Mock(
                    parts=[
                        Mock(text="Some text", inline_data=None),
                        Mock(text=None, inline_data=Mock(data=image_data)),
                    ]
                )
            )
        ]

        result = ai_client.extract_image_from_response(mock_response)
        assert result == image_data

    def test_extract_image_from_response_no_image(self, ai_client: AIClient) -> None:
        """Test image extraction when no image present."""
        mock_response = Mock()
        mock_response.candidates = [
            Mock(
                content=Mock(
                    parts=[
                        Mock(text="Only text", inline_data=None),
                    ]
                )
            )
        ]

        result = ai_client.extract_image_from_response(mock_response)
        assert result is None

    def test_validate_model_name(self, ai_client: AIClient) -> None:
        """Test model name validation."""
        # Valid models
        assert ai_client.validate_model_name("gemini-2.5-flash") is True
        assert ai_client.validate_model_name("gemini-2.5-flash-image-preview") is True
        assert ai_client.validate_model_name("veo-3.0-generate-001") is True

        # Invalid models
        assert ai_client.validate_model_name("invalid-model") is False
        assert ai_client.validate_model_name("") is False
        assert ai_client.validate_model_name(None) is False  # type: ignore


class TestAIClientStructuredOutput:
    """Test structured output functionality."""

    @pytest.fixture
    def ai_client(self) -> AIClient:
        """Create AI client instance for testing."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            client = AIClient()
            client.client = Mock(spec=genai.Client)
            return client

    def test_generate_structured_output(self, ai_client: AIClient) -> None:
        """Test structured output generation."""
        mock_response = Mock()
        mock_response.candidates = [
            Mock(
                content=Mock(
                    parts=[
                        Mock(
                            text='{"title": "Test", "steps": ["Step 1", "Step 2"]}',
                            inline_data=None,
                        )
                    ]
                )
            )
        ]

        ai_client.client.models.generate_content.return_value = mock_response

        result = ai_client.generate_structured_output(
            model="gemini-2.5-flash",
            prompt="Generate tutorial",
            response_schema={
                "type": "object",
                "properties": {"title": {"type": "string"}},
            },
        )

        assert result == {"title": "Test", "steps": ["Step 1", "Step 2"]}

        # Verify the call included response_mime_type
        call_args = ai_client.client.models.generate_content.call_args
        assert call_args[1].get("response_mime_type") == "application/json"

    def test_generate_structured_output_invalid_json(self, ai_client: AIClient) -> None:
        """Test handling of invalid JSON in structured output."""
        mock_response = Mock()
        mock_response.candidates = [
            Mock(content=Mock(parts=[Mock(text="Invalid JSON {[", inline_data=None)]))
        ]

        ai_client.client.models.generate_content.return_value = mock_response

        with pytest.raises(AIClientAPIError) as exc_info:
            ai_client.generate_structured_output(
                model="gemini-2.5-flash", prompt="Generate tutorial", response_schema={}
            )
        assert "Failed to parse JSON response" in str(exc_info.value)
