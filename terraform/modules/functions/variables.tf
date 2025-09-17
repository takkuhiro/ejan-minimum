# Variables for Functions module

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
}

variable "google_api_key" {
  description = "Google API Key for AI services"
  type        = string
  sensitive   = true
}

variable "storage_bucket_name" {
  description = "Name of the storage bucket for media files"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for functions"
  type        = string
}

variable "max_instances" {
  description = "Maximum number of function instances"
  type        = number
  default     = 10
}

variable "force_destroy" {
  description = "Allow destruction of storage bucket (dev only)"
  type        = bool
  default     = false
}