# Outputs for Functions module

output "video_generation_function_url" {
  description = "Video generation Cloud Function URL"
  value       = google_cloudfunctions2_function.video_generation.service_config[0].uri
}

output "video_generation_function_name" {
  description = "Video generation Cloud Function name"
  value       = google_cloudfunctions2_function.video_generation.name
}

output "function_source_bucket_name" {
  description = "Function source bucket name"
  value       = google_storage_bucket.function_source.name
}