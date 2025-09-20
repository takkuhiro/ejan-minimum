# Cloud Storage Bucket for storing images and videos
resource "google_storage_bucket" "main" {
  name          = "ejan-minimum-storage-${var.environment}"
  location      = var.location
  force_destroy = var.force_destroy

  # CORS configuration for web access
  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # Lifecycle rules for auto-deletion
  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_age > 0 ? [1] : []
    content {
      condition {
        age = var.lifecycle_age
      }
      action {
        type = "Delete"
      }
    }
  }

  versioning {
    enabled = var.versioning_enabled
  }

  labels = {
    environment = var.environment
    project     = "ejan-minimum"
    managed_by  = "terraform"
    module      = "storage"
  }
}

# Make bucket publicly readable
resource "google_storage_bucket_iam_member" "public_viewer" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}