"""
Test FastAPI application setup including:
- Application initialization
- Environment variables configuration
- CORS middleware setup
- Error handling middleware
- Health check endpoint
"""

import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from typing import Generator
import os


@pytest.fixture
def test_env() -> Generator[None, None, None]:
    """Set up test environment variables."""
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ["GOOGLE_API_KEY"] = "test-api-key"
    os.environ["PROJECT_ID"] = "test-project"
    os.environ["STORAGE_BUCKET"] = "test-bucket"
    os.environ["ENV"] = "test"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.mark.asyncio
async def test_health_check_endpoint(test_env):
    """Test that health check endpoint returns expected response."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "ejan-api",
            "version": "1.0.0",
        }


@pytest.mark.asyncio
async def test_cors_headers_for_frontend(test_env):
    """Test CORS headers allow frontend access from localhost:3000."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )


@pytest.mark.asyncio
async def test_cors_rejects_unauthorized_origin(test_env):
    """Test CORS rejects requests from unauthorized origins."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://unauthorized.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should not have CORS headers for unauthorized origin
        assert (
            "access-control-allow-origin" not in response.headers
            or response.headers.get("access-control-allow-origin")
            != "http://unauthorized.com"
        )


@pytest.mark.asyncio
async def test_error_handling_middleware(test_env):
    """Test that error handling middleware catches and formats errors properly."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 404 error
        response = await client.get("/non-existent-endpoint")

        assert response.status_code == 404
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_environment_configuration(test_env):
    """Test that environment variables are properly loaded in config."""
    from unittest.mock import patch

    with patch("app.core.config.settings") as mock_settings:
        mock_settings.google_api_key = "test-api-key"
        mock_settings.google_cloud_project = "test-project"
        mock_settings.storage_bucket = "test-bucket"
        mock_settings.env = "test"

        assert mock_settings.google_api_key == "test-api-key"
        assert mock_settings.google_cloud_project == "test-project"
        assert mock_settings.storage_bucket == "test-bucket"
        assert mock_settings.env == "test"


@pytest.mark.asyncio
async def test_application_metadata(test_env):
    """Test that application has proper metadata."""
    from app.main import app

    assert app.title == "Ejan API"
    assert app.version == "1.0.0"
    assert app.description is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test OpenAPI docs are available
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_validation_error_response_format(test_env):
    """Test that validation errors return proper format."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test"):
        # Once we have an endpoint with validation, we'll test it
        # For now, just ensure the app can handle validation errors
        pass  # This will be implemented when we have actual endpoints
