terraform {
  required_version = ">= 1.5.0"

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

  # Backend configuration for state storage
  # Uncomment and configure for remote state management
  # backend "gcs" {
  #   bucket = "ejan-minimum-terraform-state"
  #   prefix = "dev"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage-api.googleapis.com",
    "iam.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com"
    # "cloudrun.googleapis.com"  # 個別に有効化が必要
  ])

  service            = each.value
  disable_on_destroy = false
}

# Storage module
module "storage" {
  source = "../../modules/storage"

  project_id         = var.project_id
  environment        = local.environment
  location           = var.storage_location
  force_destroy      = true  # Allow destruction in dev environment
  versioning_enabled = false # Disable versioning in dev to save costs
  lifecycle_age      = 30    # Auto-delete objects after 30 days in dev
  cors_origins       = ["http://localhost:3000", "http://localhost:3001", "https://*.vercel.app"]

  depends_on = [google_project_service.required_apis]
}

# IAM module
module "iam" {
  source = "../../modules/iam"

  project_id  = var.project_id
  environment = local.environment
  bucket_name = module.storage.bucket_name

  depends_on = [
    google_project_service.required_apis,
    module.storage
  ]
}

# Functions module
module "functions" {
  source = "../../modules/functions"

  project_id            = var.project_id
  environment           = local.environment
  region                = var.region
  google_api_key        = var.google_api_key
  storage_bucket_name   = module.storage.bucket_name
  service_account_email = module.iam.service_account_email
  force_destroy         = true # Allow destruction in dev environment

  depends_on = [
    google_project_service.required_apis,
    module.storage,
    module.iam
  ]
}

locals {
  environment = "dev"
}