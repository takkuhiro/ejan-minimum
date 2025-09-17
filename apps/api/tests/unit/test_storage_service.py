"""Tests for Storage service functionality."""

import io
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.services.storage import StorageService


class TestStorageService:
    """Test Storage service for file upload and management."""

    @pytest.fixture
    def mock_storage_client(self):
        """Create a mock storage client."""
        with patch("app.services.storage.StorageClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_client.get_bucket.return_value = mock_bucket
            mock_client_cls.return_value = mock_client
            yield mock_client, mock_bucket

    def test_service_initialization(self, mock_storage_client):
        """Test that StorageService can be initialized."""
        service = StorageService()
        assert service is not None

    def test_generate_unique_filename(self, mock_storage_client):
        """Test unique filename generation."""
        service = StorageService()

        # Test with different prefixes and extensions
        filename1 = service.generate_unique_filename("image", "jpg")
        filename2 = service.generate_unique_filename("video", "mp4")

        # Check format
        assert filename1.startswith("image_")
        assert filename1.endswith(".jpg")
        assert filename2.startswith("video_")
        assert filename2.endswith(".mp4")

        # Check uniqueness
        assert filename1 != filename2

        # Same prefix should still generate unique names
        filename3 = service.generate_unique_filename("image", "jpg")
        assert filename1 != filename3

    def test_upload_image_jpeg(self, mock_storage_client):
        """Test uploading JPEG image."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/image_123.jpg"

        service = StorageService()
        image_data = b"fake_image_data"

        # Upload image
        url = service.upload_image(image_data, "image/jpeg")

        # Verify blob creation and upload
        assert url == "https://storage.googleapis.com/test-bucket/image_123.jpg"
        mock_bucket.blob.assert_called_once()
        mock_blob.upload_from_file.assert_called_once()
        mock_blob.make_public.assert_called_once()

    def test_upload_image_png(self, mock_storage_client):
        """Test uploading PNG image."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/image_456.png"

        service = StorageService()
        image_data = b"fake_png_data"

        url = service.upload_image(image_data, "image/png")

        assert url == "https://storage.googleapis.com/test-bucket/image_456.png"
        assert mock_blob.content_type == "image/png"

    def test_upload_image_webp(self, mock_storage_client):
        """Test uploading WebP image."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/image_789.webp"

        service = StorageService()
        image_data = b"fake_webp_data"

        url = service.upload_image(image_data, "image/webp")

        assert url == "https://storage.googleapis.com/test-bucket/image_789.webp"
        assert mock_blob.content_type == "image/webp"

    def test_upload_image_unsupported_format(self, mock_storage_client):
        """Test uploading unsupported image format raises error."""
        service = StorageService()
        image_data = b"fake_data"

        with pytest.raises(ValueError, match="Unsupported image format"):
            service.upload_image(image_data, "image/bmp")

    def test_upload_video_mp4(self, mock_storage_client):
        """Test uploading MP4 video."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/video_123.mp4"

        service = StorageService()
        video_data = b"fake_video_data"

        url = service.upload_video(video_data, "video/mp4")

        assert url == "https://storage.googleapis.com/test-bucket/video_123.mp4"
        assert mock_blob.content_type == "video/mp4"
        mock_blob.make_public.assert_called_once()

    def test_upload_video_unsupported_format(self, mock_storage_client):
        """Test uploading unsupported video format raises error."""
        service = StorageService()
        video_data = b"fake_data"

        with pytest.raises(ValueError, match="Unsupported video format"):
            service.upload_video(video_data, "video/avi")

    def test_upload_retry_on_failure(self, mock_storage_client):
        """Test retry logic on upload failure."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Simulate failure then success
        mock_blob.upload_from_file.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            None,  # Success on third try
        ]
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/image_retry.jpg"

        service = StorageService()
        image_data = b"fake_image_data"

        # Should succeed after retries
        url = service.upload_image(image_data, "image/jpeg")

        assert url == "https://storage.googleapis.com/test-bucket/image_retry.jpg"
        assert mock_blob.upload_from_file.call_count == 3

    def test_upload_max_retries_exceeded(self, mock_storage_client):
        """Test that max retries raises error."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Always fail
        mock_blob.upload_from_file.side_effect = Exception("Persistent error")

        service = StorageService()
        image_data = b"fake_image_data"

        with pytest.raises(Exception, match="Failed to upload after"):
            service.upload_image(image_data, "image/jpeg")

        # Should have tried 3 times
        assert mock_blob.upload_from_file.call_count == 3

    def test_get_public_url(self, mock_storage_client):
        """Test getting public URL for uploaded file."""
        mock_client, mock_bucket = mock_storage_client

        service = StorageService()
        filename = "test/path/image.jpg"

        with patch.dict("os.environ", {"STORAGE_BUCKET": "my-bucket"}):
            url = service.get_public_url(filename)

        assert url == "https://storage.googleapis.com/my-bucket/test/path/image.jpg"

    def test_file_exists_check(self, mock_storage_client):
        """Test checking if file exists in storage."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob

        service = StorageService()
        exists = service.file_exists("test/image.jpg")

        assert exists is True
        mock_bucket.blob.assert_called_once_with("test/image.jpg")
        mock_blob.exists.assert_called_once()

    def test_delete_file(self, mock_storage_client):
        """Test deleting a file from storage."""
        mock_client, mock_bucket = mock_storage_client
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        service = StorageService()
        success = service.delete_file("test/image.jpg")

        assert success is True
        mock_blob.delete.assert_called_once()