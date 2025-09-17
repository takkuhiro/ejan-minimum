output "service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.main.email
}

output "service_account_id" {
  description = "The ID of the service account"
  value       = google_service_account.main.id
}

output "service_account_name" {
  description = "The fully qualified name of the service account"
  value       = google_service_account.main.name
}

output "service_account_key" {
  description = "The base64 encoded service account key"
  value       = google_service_account_key.main.private_key
  sensitive   = true
}