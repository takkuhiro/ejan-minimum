# Service Account for EJAN Minimum application
resource "google_service_account" "main" {
  account_id   = "ejan-minimum-${var.environment}-sa"
  display_name = "EJAN Minimum ${var.environment} Service Account"
  description  = "Service account for EJAN Minimum application in ${var.environment} environment"
  project      = var.project_id
}

# Generate and download service account key
resource "google_service_account_key" "main" {
  service_account_id = google_service_account.main.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Grant Storage Admin role to service account for the bucket
resource "google_storage_bucket_iam_member" "storage_admin" {
  bucket = var.bucket_name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.main.email}"
}

# Additional IAM roles for the service account at project level
resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.main.email}"
}

# Grant AI Platform User role for using Gemini, Nano Banana, and Veo3
resource "google_project_iam_member" "ai_platform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.main.email}"
}

# Grant Cloud Functions Invoker role (for future use)
resource "google_project_iam_member" "functions_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.main.email}"
}