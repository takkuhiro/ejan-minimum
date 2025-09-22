# Cloud Functions用のリソース定義

# Cloud Functionsソースファイル用のZIPアーカイブ
data "archive_file" "video_generation_source" {
  type        = "zip"
  output_path = "video_generation_function.zip"
  source_dir  = "../apps/functions/video_generation"
  excludes = [
    "venv",
    "tests",
    "__pycache__",
    "*.pyc",
    ".pytest_cache"
  ]
}

# Cloud Storageバケット（Functionソースコード用）
resource "google_storage_bucket" "function_source" {
  name          = "${var.project_id}-function-source"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# Functionソースコードのアップロード
resource "google_storage_bucket_object" "video_generation_source" {
  name   = "video_generation_function.${data.archive_file.video_generation_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.video_generation_source.output_path
}

# Cloud Functions (Gen 2)
resource "google_cloudfunctions2_function" "video_generation" {
  name        = "video-generation"
  location    = var.region
  description = "Veo3を使用した動画生成Function"

  build_config {
    runtime     = "python312"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.video_generation_source.name
      }
    }
  }

  service_config {
    max_instance_count               = 10
    min_instance_count               = 0
    available_memory                 = "4Gi"
    timeout_seconds                  = 540
    max_instance_request_concurrency = 1
    available_cpu                    = "2"

    environment_variables = {
      GOOGLE_API_KEY = var.google_api_key
      STORAGE_BUCKET = google_storage_bucket.media_storage.name
    }

    service_account_email = data.google_service_account.ejan_minimum_dev_sa.email
  }

  depends_on = [
    google_storage_bucket_object.video_generation_source
  ]
}

# Function実行権限の設定（認証なしで実行可能）
resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = google_cloudfunctions2_function.video_generation.project
  location       = google_cloudfunctions2_function.video_generation.location
  cloud_function = google_cloudfunctions2_function.video_generation.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}