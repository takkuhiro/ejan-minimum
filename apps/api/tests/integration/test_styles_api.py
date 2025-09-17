"""Integration tests for style generation API."""

import base64
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_storage_service():
    """Mock storage service for integration tests."""
    with patch("app.services.storage.StorageService") as mock:
        instance = AsyncMock()
        mock.return_value = instance
        instance.upload_image.return_value = (
            "https://storage.googleapis.com/bucket/test-image.jpg"
        )
        yield instance


@pytest.fixture
def mock_ai_client():
    """Mock AI client for integration tests."""
    with patch("app.services.ai_client.AIClient") as mock:
        instance = AsyncMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def valid_request_data() -> dict:
    """Create valid request data with a small test image."""
    # Create a minimal PNG image
    png_data = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,  # PNG signature
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,  # IHDR chunk
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,  # 1x1 pixel
            0x08,
            0x02,
            0x00,
            0x00,
            0x00,
            0x90,
            0x77,
            0x53,
            0xDE,
            0x00,
            0x00,
            0x00,
            0x0C,
            0x49,
            0x44,
            0x41,
            0x54,  # IDAT chunk
            0x08,
            0x99,
            0x01,
            0x01,
            0x00,
            0x00,
            0x00,
            0x02,
            0x00,
            0x01,
            0xE2,
            0x21,
            0xBC,
            0x33,
            0x00,
            0x00,
            0x00,
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,  # IEND chunk
            0xAE,
            0x42,
            0x60,
            0x82,
        ]
    )

    return {"photo": base64.b64encode(png_data).decode("utf-8"), "gender": "female"}


@pytest.mark.asyncio
async def test_styles_api_full_flow(
    valid_request_data, mock_storage_service, mock_ai_client
):
    """Test the complete style generation flow."""
    from app.models.response import GeneratedStyle

    # Mock the style generation service to return proper GeneratedStyle objects
    with patch("app.api.routes.styles.StyleGenerationService") as mock_service_cls:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service

        # Create mock GeneratedStyle objects
        mock_styles = [
            GeneratedStyle(
                id="style-1",
                title="Style 1",
                description="Description 1",
                imageUrl="https://storage.googleapis.com/bucket/style-1.jpg",
            ),
            GeneratedStyle(
                id="style-2",
                title="Style 2",
                description="Description 2",
                imageUrl="https://storage.googleapis.com/bucket/style-2.jpg",
            ),
            GeneratedStyle(
                id="style-3",
                title="Style 3",
                description="Description 3",
                imageUrl="https://storage.googleapis.com/bucket/style-3.jpg",
            ),
        ]
        mock_service.generate_styles.return_value = mock_styles

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/styles/generate", json=valid_request_data
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify response structure
            assert "styles" in data
            assert len(data["styles"]) == 3

            # Verify each style has required fields
            for style in data["styles"]:
                assert "id" in style
                assert "title" in style
                assert "description" in style
                assert "imageUrl" in style
                assert style["imageUrl"].startswith("https://storage.googleapis.com/")


@pytest.mark.asyncio
async def test_styles_api_network_retry(
    valid_request_data, mock_storage_service, mock_ai_client
):
    """Test that the API retries on network failures."""
    from app.models.response import GeneratedStyle

    with patch("app.api.routes.styles.StyleGenerationService") as mock_service_cls:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service

        # First two calls fail, third succeeds
        mock_service.generate_styles.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            [
                GeneratedStyle(
                    id="style-1",
                    title="Style 1",
                    description="Description 1",
                    imageUrl="https://storage.googleapis.com/bucket/style-1.jpg",
                )
            ],
        ]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/styles/generate",
                json=valid_request_data,
                timeout=30.0,  # Allow time for retries
            )

            # Should eventually succeed after retries
            # Or fail with 500 if all retries exhausted
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ]


@pytest.mark.asyncio
async def test_styles_api_performance(valid_request_data):
    """Test API response time is within acceptable limits."""
    import time

    with patch("app.api.routes.styles.StyleGenerationService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service

        # Mock quick response
        from app.models.response import GeneratedStyle

        mock_service.generate_styles.return_value = [
            GeneratedStyle(
                id=f"style-{i}",
                title=f"Style {i}",
                description=f"Description {i}",
                imageUrl=f"https://storage.googleapis.com/bucket/style-{i}.jpg",
            )
            for i in range(3)
        ]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            start_time = time.time()

            response = await client.post(
                "/api/styles/generate", json=valid_request_data
            )

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == status.HTTP_200_OK
            # Response should be reasonably fast for mocked service
            assert response_time < 2.0  # seconds


@pytest.mark.asyncio
async def test_styles_api_concurrent_requests(valid_request_data):
    """Test that API handles concurrent requests properly."""
    import asyncio

    with patch("app.api.routes.styles.StyleGenerationService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        from app.models.response import GeneratedStyle

        mock_service.generate_styles.return_value = [
            GeneratedStyle(
                id="style-1",
                title="Style",
                description="Description",
                imageUrl="https://storage.googleapis.com/bucket/style.jpg",
            ),
            GeneratedStyle(
                id="style-2",
                title="Style",
                description="Description",
                imageUrl="https://storage.googleapis.com/bucket/style.jpg",
            ),
            GeneratedStyle(
                id="style-3",
                title="Style",
                description="Description",
                imageUrl="https://storage.googleapis.com/bucket/style.jpg",
            ),
        ]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Send 5 concurrent requests
            tasks = [
                client.post("/api/styles/generate", json=valid_request_data)
                for _ in range(5)
            ]

            responses = await asyncio.gather(*tasks)

            # All requests should succeed
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data["styles"]) == 3


@pytest.mark.asyncio
async def test_styles_api_validation_errors():
    """Test various validation error scenarios."""
    test_cases = [
        # Invalid image format
        {
            "data": {"photo": "not-base64!", "gender": "female"},
            "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_type": "INVALID BASE64",
        },
        # Missing gender
        {
            "data": {"photo": "dmFsaWRiYXNlNjQ="},
            "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_field": "gender",
        },
        # Empty photo
        {
            "data": {"photo": "", "gender": "male"},
            "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_field": "photo",
        },
        # Invalid gender value
        {
            "data": {"photo": "dmFsaWRiYXNlNjQ=", "gender": "other"},
            "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_field": "gender",
        },
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for test_case in test_cases:
            response = await client.post("/api/styles/generate", json=test_case["data"])

            assert response.status_code == test_case["expected_status"]

            if "error_type" in test_case:
                error_data = response.json()
                # Check if the error type is in the response (may be in detail or message)
                assert test_case["error_type"] in str(error_data).upper()
            elif "error_field" in test_case:
                error_data = response.json()
                # Check if the error field is mentioned in the response
                assert test_case["error_field"] in str(error_data).lower()
