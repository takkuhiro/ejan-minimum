"""Integration tests for tutorial generation endpoints."""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.response import TutorialResponse, TutorialStep


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as client:
        yield client


@pytest.fixture
def mock_tutorial_service():
    """Mock tutorial generation service."""
    with patch("app.api.routes.tutorials.TutorialGenerationService") as mock_service:
        instance = mock_service.return_value
        yield instance


@pytest.fixture
def sample_tutorial_request() -> Dict[str, Any]:
    """Sample tutorial generation request data."""
    return {
        "style_id": "style_123",
        "customization_text": "Add more focus on eye makeup",
    }


@pytest.fixture
def sample_tutorial_response() -> TutorialResponse:
    """Sample tutorial response."""
    steps = [
        TutorialStep(
            step_number=1,
            title="Base makeup preparation",
            description="Start with clean, moisturized face",
            image_url="https://storage.googleapis.com/bucket/step1.png",
            video_url="https://storage.googleapis.com/bucket/step1.mp4",
            tools=["Moisturizer", "Primer"],
        ),
        TutorialStep(
            step_number=2,
            title="Foundation application",
            description="Apply foundation evenly across face",
            image_url="https://storage.googleapis.com/bucket/step2.png",
            video_url="https://storage.googleapis.com/bucket/step2.mp4",
            tools=["Foundation", "Beauty blender"],
        ),
        TutorialStep(
            step_number=3,
            title="Eye makeup",
            description="Apply eyeshadow and eyeliner",
            image_url="https://storage.googleapis.com/bucket/step3.png",
            video_url="https://storage.googleapis.com/bucket/step3.mp4",
            tools=["Eyeshadow palette", "Eyeliner", "Brushes"],
        ),
    ]

    return TutorialResponse(
        id="tutorial_456",
        title="Natural Glam Makeup Tutorial",
        description="Step-by-step guide to achieve natural glam look",
        total_steps=3,
        steps=steps,
    )


class TestGetTutorialEndpoint:
    """Test get tutorial endpoint."""

    def test_get_tutorial_success(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_response: TutorialResponse,
    ):
        """Test successful tutorial retrieval."""
        # Setup mock
        mock_tutorial_service.get_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        # Make request
        response = client.get("/api/tutorials/tutorial_456")

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "tutorial_456"
        assert data["title"] == "Natural Glam Makeup Tutorial"
        assert len(data["steps"]) == 3

        # Verify mock was called correctly
        mock_tutorial_service.get_tutorial.assert_called_once_with("tutorial_456")

    def test_get_tutorial_not_found(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
    ):
        """Test tutorial not found."""
        # Setup mock
        mock_tutorial_service.get_tutorial = AsyncMock(
            side_effect=ValueError("Tutorial tutorial_999 not found")
        )

        # Make request
        response = client.get("/api/tutorials/tutorial_999")

        # Verify response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error"] == "tutorial_not_found"
        assert "tutorial_999" in data["detail"]["message"]

    def test_get_tutorial_server_error(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
    ):
        """Test server error during tutorial retrieval."""
        # Setup mock
        mock_tutorial_service.get_tutorial = AsyncMock(
            side_effect=Exception("Storage connection failed")
        )

        # Make request
        response = client.get("/api/tutorials/tutorial_456")

        # Verify response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"]["error"] == "tutorial_retrieval_failed"
        assert "Storage connection failed" in data["detail"]["message"]


class TestTutorialGenerationEndpoint:
    """Test tutorial generation endpoint."""

    def test_generate_tutorial_success(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_request: Dict[str, Any],
        sample_tutorial_response: TutorialResponse,
    ):
        """Test successful tutorial generation."""
        # Setup mock
        mock_tutorial_service.generate_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        # Make request
        response = client.post("/api/tutorials/generate", json=sample_tutorial_request)

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_tutorial_response.id
        assert data["title"] == sample_tutorial_response.title
        assert data["description"] == sample_tutorial_response.description
        assert data["total_steps"] == sample_tutorial_response.total_steps
        assert len(data["steps"]) == 3

        # Verify first step
        first_step = data["steps"][0]
        assert first_step["step_number"] == 1
        assert first_step["title"] == "Base makeup preparation"
        assert first_step["image_url"].startswith("https://")
        assert first_step["video_url"].startswith("https://")
        assert len(first_step["tools"]) == 2

    def test_generate_tutorial_without_customization(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_response: TutorialResponse,
    ):
        """Test tutorial generation without customization text."""
        # Setup mock
        mock_tutorial_service.generate_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        # Make request without customization_text
        request_data = {"style_id": "style_123"}

        response = client.post("/api/tutorials/generate", json=request_data)

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_tutorial_response.id

        # Verify mock was called correctly
        mock_tutorial_service.generate_tutorial.assert_called_once()
        call_args = mock_tutorial_service.generate_tutorial.call_args
        assert call_args[1]["style_id"] == "style_123"
        assert call_args[1].get("customization_text") is None

    def test_generate_tutorial_invalid_request(
        self, client: TestClient, mock_tutorial_service: MagicMock
    ):
        """Test tutorial generation with invalid request."""
        # Make request without required style_id
        request_data = {"customization_text": "Some text"}

        response = client.post("/api/tutorials/generate", json=request_data)

        # Verify error response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

        # Verify service was not called
        mock_tutorial_service.generate_tutorial.assert_not_called()

    def test_generate_tutorial_customization_too_long(
        self, client: TestClient, mock_tutorial_service: MagicMock
    ):
        """Test tutorial generation with customization text exceeding limit."""
        # Create text longer than 1000 characters
        long_text = "x" * 1001

        request_data = {"style_id": "style_123", "customization_text": long_text}

        response = client.post("/api/tutorials/generate", json=request_data)

        # Verify error response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

        # Verify service was not called
        mock_tutorial_service.generate_tutorial.assert_not_called()

    def test_generate_tutorial_service_error(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_request: Dict[str, Any],
    ):
        """Test tutorial generation when service raises error."""
        # Setup mock to raise exception
        mock_tutorial_service.generate_tutorial = AsyncMock(
            side_effect=ValueError("Failed to generate tutorial")
        )

        # Make request
        response = client.post("/api/tutorials/generate", json=sample_tutorial_request)

        # Verify error response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "tutorial_generation_failed" in str(data["detail"])
        assert "Failed to generate tutorial" in str(data["detail"])

    def test_generate_tutorial_timeout(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_request: Dict[str, Any],
    ):
        """Test tutorial generation timeout handling."""
        # Setup mock to raise timeout error
        mock_tutorial_service.generate_tutorial = AsyncMock(
            side_effect=asyncio.TimeoutError("Generation timeout")
        )

        # Make request
        response = client.post("/api/tutorials/generate", json=sample_tutorial_request)

        # Verify error response
        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        data = response.json()
        assert "detail" in data
        assert "timeout" in str(data["detail"]).lower()

    @pytest.mark.asyncio
    async def test_generate_tutorial_async(
        self,
        async_client: AsyncClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_request: Dict[str, Any],
        sample_tutorial_response: TutorialResponse,
    ):
        """Test async tutorial generation."""
        # Setup mock
        mock_tutorial_service.generate_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        # Make async request
        response = await async_client.post(
            "/api/tutorials/generate", json=sample_tutorial_request
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_tutorial_response.id
        assert len(data["steps"]) == 3

        # Verify all steps have required fields
        for i, step in enumerate(data["steps"]):
            assert step["step_number"] == i + 1
            assert "title" in step
            assert "description" in step
            assert "image_url" in step
            assert "video_url" in step
            assert "tools" in step
            assert isinstance(step["tools"], list)

    def test_generate_tutorial_empty_style_id(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_response: TutorialResponse,
    ):
        """Test tutorial generation with empty style ID."""
        # Setup mock
        mock_tutorial_service.generate_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        request_data = {"style_id": ""}

        response = client.post("/api/tutorials/generate", json=request_data)

        # Empty string is technically valid, the service will handle validation
        assert response.status_code == status.HTTP_200_OK
        mock_tutorial_service.generate_tutorial.assert_called_once()

    def test_generate_tutorial_concurrent_requests(
        self,
        client: TestClient,
        mock_tutorial_service: MagicMock,
        sample_tutorial_response: TutorialResponse,
    ):
        """Test concurrent tutorial generation requests."""
        import threading

        # Setup mock
        mock_tutorial_service.generate_tutorial = AsyncMock(
            return_value=sample_tutorial_response
        )

        results = []
        errors = []

        def make_request(style_id: str):
            try:
                response = client.post(
                    "/api/tutorials/generate", json={"style_id": style_id}
                )
                results.append(response)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(f"style_{i}",))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all requests succeeded
        assert len(errors) == 0
        assert len(results) == 5

        for response in results:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == sample_tutorial_response.id


class TestTutorialResponseValidation:
    """Test tutorial response validation."""

    def test_valid_tutorial_response(self):
        """Test creating a valid tutorial response."""
        steps = [
            TutorialStep(
                step_number=1,
                title="Step 1",
                description="First step",
                image_url="https://example.com/img1.jpg",
                video_url="https://example.com/vid1.mp4",
                tools=["Tool 1"],
            )
        ]

        response = TutorialResponse(
            id="tutorial_1",
            title="Test Tutorial",
            description="A test tutorial",
            total_steps=1,
            steps=steps,
        )

        assert response.id == "tutorial_1"
        assert response.total_steps == 1
        assert len(response.steps) == 1

    def test_tutorial_response_step_count_mismatch(self):
        """Test tutorial response with mismatched step count."""
        steps = [
            TutorialStep(
                step_number=1,
                title="Step 1",
                description="First step",
                image_url="https://example.com/img1.jpg",
                video_url="https://example.com/vid1.mp4",
                tools=[],
            )
        ]

        # Should raise validation error
        with pytest.raises(ValueError) as exc_info:
            TutorialResponse(
                id="tutorial_1",
                title="Test Tutorial",
                description="A test tutorial",
                total_steps=2,  # Mismatch: only 1 step provided
                steps=steps,
            )

        assert "total_steps" in str(exc_info.value)
        assert "must match" in str(exc_info.value)

    def test_tutorial_step_invalid_urls(self):
        """Test tutorial step with invalid URLs."""
        # Invalid image URL
        with pytest.raises(ValueError):
            TutorialStep(
                step_number=1,
                title="Step 1",
                description="First step",
                image_url="not-a-url",
                video_url="https://example.com/vid1.mp4",
                tools=[],
            )

        # Invalid video URL
        with pytest.raises(ValueError):
            TutorialStep(
                step_number=1,
                title="Step 1",
                description="First step",
                image_url="https://example.com/img1.jpg",
                video_url="ftp://example.com/vid1.mp4",  # Wrong protocol
                tools=[],
            )

    def test_tutorial_step_negative_number(self):
        """Test tutorial step with negative step number."""
        with pytest.raises(ValueError):
            TutorialStep(
                step_number=-1,  # Invalid: must be positive
                title="Step 1",
                description="First step",
                image_url="https://example.com/img1.jpg",
                video_url="https://example.com/vid1.mp4",
                tools=[],
            )
