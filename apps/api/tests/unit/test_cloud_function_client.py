"""Unit tests for CloudFunctionClient with retry logic."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx

from app.services.cloud_function_client import CloudFunctionClient


@pytest.fixture
def cloud_function_client():
    """Create CloudFunctionClient instance."""
    return CloudFunctionClient()


@pytest.mark.asyncio
async def test_generate_video_success_first_attempt(cloud_function_client):
    """Test successful video generation on first attempt."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"video_url": "https://example.com/video.mp4"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=mock_response)

        result = await cloud_function_client.generate_video(
            image_url="https://example.com/image.jpg",
            instruction_text="Generate video",
            step_number=1,
        )

        assert result == "https://example.com/video.mp4"
        mock_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_generate_video_retry_on_429_error(cloud_function_client):
    """Test retry logic on 429 rate limit error."""
    # First two attempts fail with 429, third succeeds
    responses = [
        MagicMock(
            status_code=429,
            text="Rate limit exceeded",
            json=MagicMock(return_value={"error": "Rate limit exceeded"}),
        ),
        MagicMock(
            status_code=429,
            text="Rate limit exceeded",
            json=MagicMock(return_value={"error": "Rate limit exceeded"}),
        ),
        MagicMock(
            status_code=200,
            json=MagicMock(return_value={"video_url": "https://example.com/video.mp4"}),
        ),
    ]

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(side_effect=responses)

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new=AsyncMock()):
            result = await cloud_function_client.generate_video(
                image_url="https://example.com/image.jpg",
                instruction_text="Generate video",
                step_number=1,
            )

            assert result == "https://example.com/video.mp4"
            assert mock_instance.post.call_count == 3


@pytest.mark.asyncio
async def test_generate_video_retry_on_quota_error(cloud_function_client):
    """Test retry logic on quota exceeded error."""
    # First attempt fails with 500 and quota message, second succeeds
    responses = [
        MagicMock(
            status_code=500,
            text='{"error": "You exceeded your current quota"}',
            json=MagicMock(return_value={"error": "You exceeded your current quota"}),
        ),
        MagicMock(
            status_code=200,
            json=MagicMock(return_value={"video_url": "https://example.com/video.mp4"}),
        ),
    ]

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(side_effect=responses)

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new=AsyncMock()):
            result = await cloud_function_client.generate_video(
                image_url="https://example.com/image.jpg",
                instruction_text="Generate video",
                step_number=1,
            )

            assert result == "https://example.com/video.mp4"
            assert mock_instance.post.call_count == 2


@pytest.mark.asyncio
async def test_generate_video_max_retries_exceeded(cloud_function_client):
    """Test that max retries are respected and error is raised."""
    # All attempts fail with 429
    mock_response = MagicMock(
        status_code=429,
        text="Rate limit exceeded",
        json=MagicMock(return_value={"error": "Rate limit exceeded"}),
    )

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=mock_response)

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new=AsyncMock()):
            with pytest.raises(
                ValueError,
                match="Video generation failed after 3 retries due to rate limit",
            ):
                await cloud_function_client.generate_video(
                    image_url="https://example.com/image.jpg",
                    instruction_text="Generate video",
                    step_number=1,
                    max_retries=3,  # Reduce for faster test
                )

            assert mock_instance.post.call_count == 3


@pytest.mark.asyncio
async def test_generate_video_non_retryable_error(cloud_function_client):
    """Test that non-retryable errors are not retried."""
    # 400 Bad Request should not be retried
    mock_response = MagicMock(
        status_code=400,
        text="Bad request",
    )

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="Cloud Function returned 400"):
            await cloud_function_client.generate_video(
                image_url="https://example.com/image.jpg",
                instruction_text="Generate video",
                step_number=1,
            )

        # Should only be called once (no retries)
        mock_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_generate_video_timeout_retry(cloud_function_client):
    """Test retry logic on timeout errors."""
    # First attempt times out, second succeeds
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value

        # First call raises timeout, second returns success
        mock_instance.post = AsyncMock(
            side_effect=[
                httpx.TimeoutException("Timeout"),
                MagicMock(
                    status_code=200,
                    json=MagicMock(
                        return_value={"video_url": "https://example.com/video.mp4"}
                    ),
                ),
            ]
        )

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new=AsyncMock()):
            result = await cloud_function_client.generate_video(
                image_url="https://example.com/image.jpg",
                instruction_text="Generate video",
                step_number=1,
            )

            assert result == "https://example.com/video.mp4"
            assert mock_instance.post.call_count == 2


@pytest.mark.asyncio
async def test_generate_video_cloud_function_rate_limit_response(cloud_function_client):
    """Test handling of rate limit error from Cloud Function itself."""
    # Cloud Function returns 200 but with error in response first, then success
    responses = [
        MagicMock(
            status_code=200,
            json=MagicMock(
                return_value={"error": "rate limit exceeded", "video_url": ""}
            ),
        ),
        MagicMock(
            status_code=200,
            json=MagicMock(return_value={"video_url": "https://example.com/video.mp4"}),
        ),
    ]

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(side_effect=responses)

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new=AsyncMock()):
            result = await cloud_function_client.generate_video(
                image_url="https://example.com/image.jpg",
                instruction_text="Generate video",
                step_number=1,
            )

            assert result == "https://example.com/video.mp4"
            assert mock_instance.post.call_count == 2
