"""Unit tests for style generation endpoint."""

import base64
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def valid_image_base64() -> str:
    """Create a valid base64 encoded test image."""
    # Create a minimal PNG image (1x1 pixel)
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
            0x0D,  # IHDR chunk size
            0x49,
            0x48,
            0x44,
            0x52,  # IHDR type
            0x00,
            0x00,
            0x00,
            0x01,  # Width: 1
            0x00,
            0x00,
            0x00,
            0x01,  # Height: 1
            0x08,
            0x02,  # Bit depth: 8, Color type: 2 (RGB)
            0x00,
            0x00,
            0x00,  # Compression, Filter, Interlace
            0x90,
            0x77,
            0x53,
            0xDE,  # CRC
            0x00,
            0x00,
            0x00,
            0x0C,  # IDAT chunk size
            0x49,
            0x44,
            0x41,
            0x54,  # IDAT type
            0x08,
            0x99,
            0x01,
            0x01,  # Compressed data
            0x00,
            0x00,
            0x00,
            0x02,
            0x00,
            0x01,
            0xE2,
            0x21,
            0xBC,
            0x33,  # CRC
            0x00,
            0x00,
            0x00,
            0x00,  # IEND chunk size
            0x49,
            0x45,
            0x4E,
            0x44,  # IEND type
            0xAE,
            0x42,
            0x60,
            0x82,  # CRC
        ]
    )
    return base64.b64encode(png_data).decode("utf-8")


@pytest.fixture
def oversized_image_base64() -> str:
    """Create a base64 encoded image larger than 10MB."""
    # Create data larger than 10MB
    large_data = b"x" * (11 * 1024 * 1024)  # 11MB
    return base64.b64encode(large_data).decode("utf-8")


@pytest.mark.asyncio
async def test_generate_styles_success(valid_image_base64):
    """Test successful style generation with valid input."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Prepare request
        request_data = {"photo": valid_image_base64, "gender": "female"}

        # Mock the services
        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # Import the model to create proper instances
            from app.models.response import GeneratedStyle

            mock_service.generate_styles.return_value = [
                GeneratedStyle(
                    id="style-1",
                    title="Natural Makeup Look",
                    description="A fresh, natural makeup style",
                    imageUrl="https://storage.googleapis.com/bucket/style-1.jpg",
                ),
                GeneratedStyle(
                    id="style-2",
                    title="Evening Glamour",
                    description="Sophisticated evening makeup",
                    imageUrl="https://storage.googleapis.com/bucket/style-2.jpg",
                ),
                GeneratedStyle(
                    id="style-3",
                    title="Bold and Dramatic",
                    description="Statement makeup with bold colors",
                    imageUrl="https://storage.googleapis.com/bucket/style-3.jpg",
                ),
            ]

            # Make request
            response = await client.post("/api/styles/generate", json=request_data)

            # Assertions
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "styles" in data
            assert len(data["styles"]) == 3

            # Check first style structure
            first_style = data["styles"][0]
            assert first_style["id"] == "style-1"
            assert first_style["title"] == "Natural Makeup Look"
            assert first_style["description"] == "A fresh, natural makeup style"
            assert first_style["imageUrl"].startswith("https://storage.googleapis.com/")


@pytest.mark.asyncio
async def test_generate_styles_invalid_gender():
    """Test style generation with invalid gender value."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": "validbase64data", "gender": "invalid_gender"}

        response = await client.post("/api/styles/generate", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("gender" in str(err).lower() for err in error_detail)


@pytest.mark.asyncio
async def test_generate_styles_missing_photo():
    """Test style generation with missing photo field."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"gender": "male"}

        response = await client.post("/api/styles/generate", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("photo" in str(err).lower() for err in error_detail)


@pytest.mark.asyncio
async def test_generate_styles_oversized_image(oversized_image_base64):
    """Test style generation with image larger than 10MB."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": oversized_image_base64, "gender": "neutral"}

        response = await client.post("/api/styles/generate", json=request_data)

        # Pydantic validation returns 422 for validation errors
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        # Check that error message mentions file size
        assert any(
            "size" in str(err).lower() or "10mb" in str(err).lower()
            for err in error_detail
        )


@pytest.mark.asyncio
async def test_generate_styles_invalid_base64():
    """Test style generation with invalid base64 encoded data."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": "invalid!@#$base64", "gender": "female"}

        response = await client.post("/api/styles/generate", json=request_data)

        # Pydantic validation returns 422 for validation errors
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        # Check that error message mentions base64 or encoding
        assert any(
            "base64" in str(err).lower() or "encoding" in str(err).lower()
            for err in error_detail
        )


@pytest.mark.asyncio
async def test_generate_styles_ai_service_error(valid_image_base64):
    """Test style generation when AI service fails."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": valid_image_base64, "gender": "male"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_styles.side_effect = Exception(
                "AI service unavailable"
            )

            response = await client.post("/api/styles/generate", json=request_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            error_data = response.json()
            assert "AI service" in error_data["detail"]


@pytest.mark.asyncio
async def test_generate_styles_cors_headers(valid_image_base64):
    """Test that CORS headers are properly set."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": valid_image_base64, "gender": "female"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            mock_service.generate_styles.return_value = []

            response = await client.post(
                "/api/styles/generate",
                json=request_data,
                headers={"Origin": "http://localhost:3000"},
            )

            # Check CORS headers
            assert "access-control-allow-origin" in response.headers
            allowed_origins = response.headers["access-control-allow-origin"]
            assert allowed_origins == "http://localhost:3000"


@pytest.mark.asyncio
async def test_generate_styles_with_all_genders(valid_image_base64):
    """Test style generation with all valid gender options."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for gender in ["male", "female", "neutral"]:
            request_data = {"photo": valid_image_base64, "gender": gender}

            with patch(
                "app.api.routes.styles.StyleGenerationService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service

                from app.models.response import GeneratedStyle

                mock_service.generate_styles.return_value = [
                    GeneratedStyle(
                        id=f"style-{gender}-{i}",
                        title=f"{gender.capitalize()} Style {i}",
                        description=f"Style for {gender}",
                        imageUrl=f"https://storage.googleapis.com/bucket/style-{gender}-{i}.jpg",
                    )
                    for i in range(1, 4)
                ]

                response = await client.post("/api/styles/generate", json=request_data)

                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data["styles"]) == 3


# ================ Tests for GET /api/styles/{id} endpoint ================


@pytest.mark.asyncio
async def test_get_style_success(valid_image_base64):
    """Test successful retrieval of a style by ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First, generate styles to populate the store
        request_data = {"photo": valid_image_base64, "gender": "female"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            from app.models.response import GeneratedStyle

            test_style = GeneratedStyle(
                id="test-style-123",
                title="Test Style",
                description="A test style description with tools: brush, sponge, eyeliner",
                imageUrl="https://storage.googleapis.com/bucket/test-style.jpg",
            )

            mock_service.generate_styles.return_value = [test_style]

            # Generate styles to populate the store
            await client.post("/api/styles/generate", json=request_data)

            # Now retrieve the specific style
            response = await client.get("/api/styles/test-style-123")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "test-style-123"
            assert data["title"] == "Test Style"
            assert (
                data["description"]
                == "A test style description with tools: brush, sponge, eyeliner"
            )
            assert (
                data["imageUrl"]
                == "https://storage.googleapis.com/bucket/test-style.jpg"
            )


@pytest.mark.asyncio
async def test_get_style_not_found():
    """Test retrieval of a non-existent style."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to get a style that doesn't exist
        response = await client.get("/api/styles/non-existent-style-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        assert "non-existent-style-id" in error_data["detail"]
        assert "not found" in error_data["detail"].lower()


@pytest.mark.asyncio
async def test_get_style_after_generation(valid_image_base64):
    """Test that generated styles can be retrieved individually."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Generate multiple styles
        request_data = {"photo": valid_image_base64, "gender": "male"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            from app.models.response import GeneratedStyle

            styles = [
                GeneratedStyle(
                    id=f"style-{i}",
                    title=f"Style {i}",
                    description=f"Description for style {i} with tools",
                    imageUrl=f"https://storage.googleapis.com/bucket/style-{i}.jpg",
                )
                for i in range(1, 4)
            ]

            mock_service.generate_styles.return_value = styles

            # Generate styles
            generation_response = await client.post(
                "/api/styles/generate", json=request_data
            )
            assert generation_response.status_code == status.HTTP_200_OK

            # Retrieve each style individually
            for i in range(1, 4):
                response = await client.get(f"/api/styles/style-{i}")
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["id"] == f"style-{i}"
                assert data["title"] == f"Style {i}"
                assert data["description"] == f"Description for style {i} with tools"


@pytest.mark.asyncio
async def test_get_style_with_special_characters_in_id(valid_image_base64):
    """Test retrieval of style with special characters in ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": valid_image_base64, "gender": "neutral"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            from app.models.response import GeneratedStyle

            special_id = "style_2024-01-15_abc123"
            test_style = GeneratedStyle(
                id=special_id,
                title="Special Style",
                description="Style with special ID format",
                imageUrl="https://storage.googleapis.com/bucket/special.jpg",
            )

            mock_service.generate_styles.return_value = [test_style]

            # Generate style
            await client.post("/api/styles/generate", json=request_data)

            # Retrieve style with special characters in ID
            response = await client.get(f"/api/styles/{special_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == special_id


@pytest.mark.asyncio
async def test_get_style_memory_persistence(valid_image_base64):
    """Test that styles persist in memory across multiple requests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_data = {"photo": valid_image_base64, "gender": "female"}

        with patch(
            "app.api.routes.styles.StyleGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            from app.models.response import GeneratedStyle

            persistent_style = GeneratedStyle(
                id="persistent-style",
                title="Persistent Style",
                description="This style should persist in memory",
                imageUrl="https://storage.googleapis.com/bucket/persistent.jpg",
            )

            mock_service.generate_styles.return_value = [persistent_style]

            # Generate style once
            await client.post("/api/styles/generate", json=request_data)

        # Try to retrieve the same style multiple times without regenerating
        for _ in range(3):
            response = await client.get("/api/styles/persistent-style")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "persistent-style"
            assert data["title"] == "Persistent Style"


@pytest.mark.asyncio
async def test_get_style_cors_headers():
    """Test that CORS headers are properly set for GET requests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to get a non-existent style (to avoid needing to generate first)
        response = await client.get(
            "/api/styles/test-style",
            headers={"Origin": "http://localhost:3000"},
        )

        # Check CORS headers even on 404 response
        assert "access-control-allow-origin" in response.headers
        allowed_origins = response.headers["access-control-allow-origin"]
        assert allowed_origins == "http://localhost:3000"
