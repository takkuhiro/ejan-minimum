# Cloud Storage リソース

# メディアファイル（画像・動画）保存用バケット
resource "google_storage_bucket" "media_storage" {
  name          = "${var.project_id}-ejan-media"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# バケットを公開読み取り可能に設定
resource "google_storage_bucket_iam_member" "media_storage_public_read" {
  bucket = google_storage_bucket.media_storage.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}