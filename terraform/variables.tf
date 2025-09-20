# 変数定義

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "asia-northeast1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "asia-northeast1-a"
}

variable "google_api_key" {
  description = "Google API Key for AI services"
  type        = string
  sensitive   = true
}