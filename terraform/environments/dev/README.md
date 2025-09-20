# Dev Environment Infrastructure

開発環境用のTerraform構成です。

## セットアップ

1. **設定ファイルの準備**
```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvarsを編集してproject_idを設定
```

2. **Terraformの初期化**
```bash
terraform init
```

3. **リソースの作成**
```bash
terraform plan
terraform apply
```

## 作成されるリソース

- **Cloud Storage バケット**: `ejan-minimum-storage-dev`
  - 30日後に自動削除
  - バージョニング無効
  - CORS設定済み

- **サービスアカウント**: `ejan-minimum-dev-sa`
  - Storage Admin権限
  - AI Platform User権限
  - Cloud Functions Invoker権限

## 出力値の利用

```bash
# バケット名を取得
terraform output storage_bucket_name

# サービスアカウントキーを保存
terraform output -raw service_account_key | base64 -d > service-account-key.json

# 環境変数に設定
export STORAGE_BUCKET=$(terraform output -raw storage_bucket_name)
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
```

## クリーンアップ

```bash
terraform destroy
```

**注意**: `force_destroy = true`が設定されているため、バケット内のデータも含めて削除されます。