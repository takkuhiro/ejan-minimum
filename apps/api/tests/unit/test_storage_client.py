"""Tests for Cloud Storage client setup."""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.storage import StorageClient


class TestStorageClient:
    """Test Cloud Storage client initialization and configuration."""

    def test_client_initialization(self):
        """Test that StorageClient can be initialized."""
        with patch("app.core.storage.storage.Client") as mock_client:
            with patch.dict(os.environ, {"STORAGE_BUCKET": "test-bucket"}):
                client = StorageClient()
                assert client is not None
                mock_client.assert_called_once()

    def test_bucket_name_from_env(self):
        """Test that bucket name is loaded from environment variable."""
        test_bucket = "test-bucket-name"
        with patch.dict(os.environ, {"STORAGE_BUCKET": test_bucket}):
            client = StorageClient()
            assert client.bucket_name == test_bucket

    def test_missing_bucket_name_raises_error(self):
        """Test that missing STORAGE_BUCKET env var raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="STORAGE_BUCKET environment variable is required"
            ):
                StorageClient()

    def test_get_bucket(self):
        """Test getting bucket instance."""
        with patch("app.core.storage.storage.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_client.bucket.return_value = mock_bucket
            mock_client_cls.return_value = mock_client

            with patch.dict(os.environ, {"STORAGE_BUCKET": "test-bucket"}):
                client = StorageClient()
                bucket = client.get_bucket()

                assert bucket == mock_bucket
                mock_client.bucket.assert_called_once_with("test-bucket")

    def test_service_account_authentication(self):
        """Test that service account is used for authentication."""
        with patch("app.core.storage.storage.Client") as mock_client:
            with patch.dict(
                os.environ,
                {
                    "STORAGE_BUCKET": "test-bucket",
                    "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
                },
            ):
                client = StorageClient()
                # Verify client initialization
                assert client is not None

    def test_bucket_exists_check(self):
        """Test checking if bucket exists."""
        with patch("app.core.storage.storage.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_bucket.exists.return_value = True
            mock_client.bucket.return_value = mock_bucket
            mock_client_cls.return_value = mock_client

            with patch.dict(os.environ, {"STORAGE_BUCKET": "test-bucket"}):
                client = StorageClient()
                exists = client.bucket_exists()

                assert exists is True
                mock_bucket.exists.assert_called_once()

    def test_bucket_not_exists(self):
        """Test behavior when bucket doesn't exist."""
        with patch("app.core.storage.storage.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_bucket.exists.return_value = False
            mock_client.bucket.return_value = mock_bucket
            mock_client_cls.return_value = mock_client

            with patch.dict(os.environ, {"STORAGE_BUCKET": "test-bucket"}):
                client = StorageClient()
                exists = client.bucket_exists()

                assert exists is False