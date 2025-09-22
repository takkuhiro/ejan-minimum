# Output値の定義

output "storage_bucket_name" {
  description = "Media storage bucket name"
  value       = google_storage_bucket.media_storage.name
}

output "storage_bucket_url" {
  description = "Media storage bucket URL"
  value       = google_storage_bucket.media_storage.url
}

output "video_generation_function_url" {
  description = "Video generation Cloud Function URL"
  value       = google_cloudfunctions2_function.video_generation.service_config[0].uri
}

output "service_account_email" {
  description = "Service account email"
  value       = data.google_service_account.ejan_minimum_dev_sa.email
}

output "service_account_key" {
  description = "Service account private key (base64 encoded)"
  value       = google_service_account_key.ejan_minimum_dev_sa_key.private_key
  sensitive   = true
}

output "api_url" {
  description = "Cloud Run API Service URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "web_url" {
  description = "Cloud Run Web Service URL"
  value       = google_cloud_run_v2_service.web.uri
}

output "artifact_registry_repo" {
  description = "Artifact Registry Repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/ejan-minimum"
}