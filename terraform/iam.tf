# IAM リソース

# ejan-minimum-dev-sa サービスアカウント
resource "google_service_account" "ejan_minimum_dev_sa" {
  account_id   = "ejan-minimum-dev-sa"
  display_name = "EJAN Minimum Development Service Account"
  description  = "Service account for EJAN application development"
}

# サービスアカウントにCloud Storageの権限を付与
resource "google_storage_bucket_iam_member" "ejan_minimum_dev_sa_storage_admin" {
  bucket = google_storage_bucket.ejan_minimum_storage_dev.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ejan_minimum_dev_sa.email}"
}

# サービスアカウントキー（開発用）
resource "google_service_account_key" "ejan_minimum_dev_sa_key" {
  service_account_id = google_service_account.ejan_minimum_dev_sa.name
}
