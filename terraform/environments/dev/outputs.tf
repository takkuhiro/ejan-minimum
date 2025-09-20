output "storage_bucket_name" {
  description = "The name of the created storage bucket"
  value       = module.storage.bucket_name
}

output "storage_bucket_url" {
  description = "The URL of the storage bucket"
  value       = module.storage.bucket_url
}

output "service_account_email" {
  description = "The email of the service account"
  value       = module.iam.service_account_email
}

output "service_account_key" {
  description = "The base64 encoded service account key"
  value       = module.iam.service_account_key
  sensitive   = true
}

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "environment" {
  description = "The deployment environment"
  value       = local.environment
}

output "video_generation_function_url" {
  description = "Video generation Cloud Function URL"
  value       = module.functions.video_generation_function_url
}

output "video_generation_function_name" {
  description = "Video generation Cloud Function name"
  value       = module.functions.video_generation_function_name
}