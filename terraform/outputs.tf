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
  value       = google_service_account.ejan_dev_sa.email
}

output "service_account_key" {
  description = "Service account private key (base64 encoded)"
  value       = google_service_account_key.ejan_dev_sa_key.private_key
  sensitive   = true
}