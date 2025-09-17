output "bucket_name" {
  description = "The name of the created storage bucket"
  value       = google_storage_bucket.main.name
}

output "bucket_url" {
  description = "The URL of the storage bucket"
  value       = google_storage_bucket.main.url
}

output "bucket_self_link" {
  description = "The self link of the bucket"
  value       = google_storage_bucket.main.self_link
}