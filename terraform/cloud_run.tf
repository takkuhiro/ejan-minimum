# Cloud Run サービス設定

# Artifact Registry リポジトリ
resource "google_artifact_registry_repository" "app_repo" {
  location      = var.region
  repository_id = "ejan-minimum"
  description   = "Docker images for EJAN minimum application"
  format        = "DOCKER"
}

# Cloud Run サービス - API
resource "google_cloud_run_v2_service" "api" {
  name     = "ejan-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/ejan-minimum/api:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "STORAGE_BUCKET"
        value = google_storage_bucket.media_storage.name
      }

      env {
        name  = "GOOGLE_API_KEY"
        value = var.google_api_key
      }

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }

      env {
        name  = "ENV"
        value = "production"
      }

      env {
        name  = "CORS_ORIGINS"
        value = "${google_cloud_run_v2_service.web.uri},http://localhost:3000"
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }

    service_account = data.google_service_account.ejan_minimum_dev_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run サービス - Web
resource "google_cloud_run_v2_service" "web" {
  name     = "ejan-web"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/ejan-minimum/web:latest"

      ports {
        container_port = 3000
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Cloud Run IAM - API (公開アクセス)
resource "google_cloud_run_service_iam_member" "api_public" {
  service  = google_cloud_run_v2_service.api.name
  location = google_cloud_run_v2_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run IAM - Web (公開アクセス)
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = google_cloud_run_v2_service.web.name
  location = google_cloud_run_v2_service.web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}