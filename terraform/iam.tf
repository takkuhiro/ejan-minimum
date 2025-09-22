# IAM リソース

# 既存のejan-minimum-dev-sa サービスアカウントを参照
data "google_service_account" "ejan_minimum_dev_sa" {
  account_id = "ejan-minimum-dev-sa"
}

# サービスアカウントにCloud Storageの権限を付与
resource "google_storage_bucket_iam_member" "ejan_minimum_dev_sa_storage_admin" {
  bucket = google_storage_bucket.media_storage.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.ejan_minimum_dev_sa.email}"
}

# サービスアカウントキー（開発用）
resource "google_service_account_key" "ejan_minimum_dev_sa_key" {
  service_account_id = data.google_service_account.ejan_minimum_dev_sa.name
}
