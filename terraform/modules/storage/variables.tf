variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "location" {
  description = "Location for Cloud Storage bucket"
  type        = string
  default     = "US"
}

variable "force_destroy" {
  description = "Whether to allow terraform to destroy the bucket even if it contains objects"
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Whether to enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "lifecycle_age" {
  description = "Age in days after which objects are deleted (0 to disable)"
  type        = number
  default     = 0
}

variable "cors_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["http://localhost:3000", "https://*.vercel.app"]
}