# Terraform設定
terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

# Google Cloud Provider設定
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}