"""Google Cloud Storage client setup and management."""

from google.cloud import storage  # type: ignore[import-untyped]
from google.cloud.storage import Bucket  # type: ignore[import-untyped]


class StorageClient:
    """Client for Google Cloud Storage operations.

    This client manages the connection to Google Cloud Storage and provides
    access to bucket operations. It uses service account authentication
    (ejan-minimum-dev-sa) for accessing GCS resources.

    Attributes:
        bucket_name: Name of the GCS bucket from STORAGE_BUCKET env var
        client: Google Cloud Storage client instance
    """

    def __init__(self) -> None:
        """Initialize Storage client with configuration.

        Raises:
            ValueError: If STORAGE_BUCKET environment variable is not set
        """
        from app.core.config import settings

        self.bucket_name: str = settings.storage_bucket
        if not self.bucket_name:
            raise ValueError("STORAGE_BUCKET environment variable is required")

        # Initialize the Google Cloud Storage client
        # Cloud Run: Uses service account attached to the service (ejan-minimum-dev-sa)
        # Local: Uses Application Default Credentials
        # Explicitly set project ID to avoid issues with credential detection
        self.client = storage.Client(project=settings.google_cloud_project)

    def get_bucket(self) -> Bucket:  # type: ignore[no-any-unimported]
        """Get the configured bucket instance.

        Returns:
            Bucket: The Google Cloud Storage bucket instance.
        """
        return self.client.bucket(self.bucket_name)

    def bucket_exists(self) -> bool:
        """Check if the configured bucket exists.

        Returns:
            bool: True if bucket exists, False otherwise.
        """
        bucket = self.get_bucket()
        return bool(bucket.exists())
