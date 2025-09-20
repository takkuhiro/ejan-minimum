variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default region for resources"
  type        = string
  default     = "us-central1"
}

variable "storage_location" {
  description = "Location for Cloud Storage bucket"
  type        = string
  default     = "US"
}

variable "google_api_key" {
  description = "Google API Key for AI services"
  type        = string
  sensitive   = true
}