"""AI client service for Gemini API integration."""

import json
import time
from typing import Any, Dict, Optional, Union, List
from google import genai
from PIL import Image


class AIClientError(Exception):
    """Base exception for AI client errors."""

    pass


class AIClientInitError(AIClientError):
    """Exception raised during AI client initialization."""

    pass


class AIClientAPIError(AIClientError):
    """Exception raised during API calls."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize API error with message and optional status code."""
        super().__init__(message)
        self.status_code = status_code


class AIClientTimeoutError(AIClientError):
    """Exception raised when API calls timeout."""

    pass


class AIClient:
    """Client for interacting with Google Generative AI (Gemini) API."""

    SUPPORTED_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-image-preview",
        "gemini-2.0-flash-lite",
        "veo-3.0-generate-001",
    ]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI client with API key.

        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY from settings.

        Raises:
            AIClientInitError: If API key is missing or client initialization fails.
        """
        from app.core.config import settings

        self.api_key = api_key or settings.google_api_key

        if not self.api_key:
            raise AIClientInitError("GOOGLE_API_KEY is not set")

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise AIClientInitError(f"Failed to initialize AI client: {e}")

    def generate_content(
        self,
        model: str,
        prompt: str,
        image: Optional[Image.Image] = None,
    ) -> Any:
        """Generate content using specified model.

        Args:
            model: Model name to use.
            prompt: Text prompt for generation.
            image: Optional PIL Image for multimodal generation.

        Returns:
            Response from the API.

        Raises:
            AIClientAPIError: If API call fails.
        """
        try:
            contents: List[Union[str, Image.Image]] = [prompt]
            if image is not None:
                contents.append(image)

            response = self.client.models.generate_content(
                model=model, contents=contents  # type: ignore[arg-type]
            )
            return response
        except Exception as e:
            raise AIClientAPIError(f"Failed to generate content: {e}")

    def generate_content_with_retry(
        self,
        model: str,
        prompt: str,
        image: Optional[Image.Image] = None,
        max_retries: int = 3,
        delay: float = 1.0,
        **kwargs: Any,
    ) -> Any:
        """Generate content with retry logic.

        Args:
            model: Model name to use.
            prompt: Text prompt for generation.
            image: Optional PIL Image for multimodal generation.
            max_retries: Maximum number of retry attempts.
            delay: Initial delay between retries in seconds.
            **kwargs: Additional parameters for the API call.

        Returns:
            Response from the API.

        Raises:
            AIClientAPIError: If all retry attempts fail.
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return self.generate_content(model, prompt, image)
            except AIClientAPIError as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(delay * (2**attempt))  # Exponential backoff
                continue

        raise AIClientAPIError(f"Failed after {max_retries} retries: {last_error}")

    def extract_text_from_response(self, response: Any) -> str:
        """Extract text content from API response.

        Args:
            response: API response object.

        Returns:
            Extracted text content.
        """
        text_parts = []

        if response and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            text_parts.append(part.text)

        return "\n".join(text_parts)

    def extract_image_from_response(self, response: Any) -> Optional[bytes]:
        """Extract image data from API response.

        Args:
            response: API response object.

        Returns:
            Image bytes if present, None otherwise.
        """
        if response and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            return part.inline_data.data  # type: ignore

        return None

    def validate_model_name(self, model: str) -> bool:
        """Validate if model name is supported.

        Args:
            model: Model name to validate.

        Returns:
            True if model is supported, False otherwise.
        """
        if not model or not isinstance(model, str):
            return False
        return model in self.SUPPORTED_MODELS

    def generate_structured_output(
        self, model: str, prompt: str, response_schema: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate structured output with JSON schema.

        Args:
            model: Model name to use.
            prompt: Text prompt for generation.
            response_schema: JSON schema for response structure.
            **kwargs: Additional parameters for the API call.

        Returns:
            Parsed JSON response.

        Raises:
            AIClientAPIError: If API call fails or response is invalid JSON.
        """
        try:
            # Note: response_mime_type and response_schema might not be in the type hints
            # but are supported in the actual API
            response = self.client.models.generate_content(  # type: ignore[call-arg]
                model=model,
                contents=prompt,  # Pass string directly, not as list
                response_mime_type="application/json",
                response_schema=response_schema,
                **kwargs,
            )

            text_response = self.extract_text_from_response(response)

            try:
                return json.loads(text_response)  # type: ignore
            except json.JSONDecodeError as e:
                raise AIClientAPIError(f"Failed to parse JSON response: {e}")

        except Exception as e:
            raise AIClientAPIError(f"Failed to generate structured output: {e}")
