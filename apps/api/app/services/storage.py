"""Storage service for file upload and management."""

import io
import os
import time
import uuid
from datetime import datetime

from app.core.storage import StorageClient


class StorageService:
    """Service for managing file uploads to Google Cloud Storage."""

    SUPPORTED_IMAGE_FORMATS = {"image/jpeg", "image/png", "image/webp"}
    SUPPORTED_VIDEO_FORMATS = {"video/mp4"}
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self) -> None:
        """Initialize storage service."""
        self.storage_client = StorageClient()

    def generate_unique_filename(self, prefix: str, extension: str) -> str:
        """Generate a unique filename with timestamp and UUID.

        Args:
            prefix: File prefix (e.g., 'image', 'video')
            extension: File extension (e.g., 'jpg', 'mp4')

        Returns:
            str: Unique filename like 'image_20240117_123456_uuid.jpg'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"

    def upload_image(self, data: bytes, content_type: str) -> str:
        """Upload image to Cloud Storage.

        Args:
            data: Image data as bytes
            content_type: MIME type of the image

        Returns:
            str: Public URL of the uploaded image

        Raises:
            ValueError: If image format is not supported
            Exception: If upload fails after retries
        """
        if content_type not in self.SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"Unsupported image format: {content_type}")

        # Determine extension from content type
        extension_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }
        extension = extension_map[content_type]

        # Generate unique filename
        filename = self.generate_unique_filename("image", extension)

        # Upload with retry logic
        return self._upload_with_retry(data, filename, content_type)

    def upload_video(self, data: bytes, content_type: str) -> str:
        """Upload video to Cloud Storage.

        Args:
            data: Video data as bytes
            content_type: MIME type of the video

        Returns:
            str: Public URL of the uploaded video

        Raises:
            ValueError: If video format is not supported
            Exception: If upload fails after retries
        """
        if content_type not in self.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(f"Unsupported video format: {content_type}")

        # Generate unique filename
        filename = self.generate_unique_filename("video", "mp4")

        # Upload with retry logic
        return self._upload_with_retry(data, filename, content_type)

    def _upload_with_retry(self, data: bytes, filename: str, content_type: str) -> str:
        """Upload file to Cloud Storage with retry logic.

        Args:
            data: File data as bytes
            filename: Filename for storage
            content_type: MIME type of the file

        Returns:
            str: Public URL of the uploaded file

        Raises:
            Exception: If upload fails after max retries
        """
        bucket = self.storage_client.get_bucket()

        for attempt in range(self.MAX_RETRIES):
            try:
                # Create blob
                blob = bucket.blob(filename)
                blob.content_type = content_type

                # Upload data
                data_stream = io.BytesIO(data)
                blob.upload_from_file(data_stream, content_type=content_type)

                # Make public for demo (in production, use signed URLs)
                blob.make_public()

                # Return public URL
                return str(blob.public_url)

            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise Exception(
                        f"Failed to upload after {self.MAX_RETRIES} attempts: {e}"
                    )
                time.sleep(self.RETRY_DELAY * (2**attempt))  # Exponential backoff
        raise Exception("Unreachable code")  # Should never get here

    def get_public_url(self, filename: str) -> str:
        """Get public URL for a file in storage.

        Args:
            filename: Path to file in bucket

        Returns:
            str: Public URL of the file
        """
        bucket_name = os.getenv("STORAGE_BUCKET")
        return f"https://storage.googleapis.com/{bucket_name}/{filename}"

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in storage.

        Args:
            filename: Path to file in bucket

        Returns:
            bool: True if file exists, False otherwise
        """
        bucket = self.storage_client.get_bucket()
        blob = bucket.blob(filename)
        return bool(blob.exists())

    def delete_file(self, filename: str) -> bool:
        """Delete a file from storage.

        Args:
            filename: Path to file in bucket

        Returns:
            bool: True if deletion successful
        """
        try:
            bucket = self.storage_client.get_bucket()
            blob = bucket.blob(filename)
            blob.delete()
            return True
        except Exception:
            return False
