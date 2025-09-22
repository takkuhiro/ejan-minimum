# EJAN Minimum Terraform Infrastructure

このディレクトリには、EJAN MinimumプロジェクトのインフラストラクチャをTerraformで管理するための設定ファイルが含まれています。

## ディレクトリ構造

```
terraform/
├── modules/              # 再利用可能なTerraformモジュール
│   ├── storage/         # Cloud Storageバケット
│   ├── iam/            # サービスアカウントとIAM
│   ├── functions/      # Cloud Functions（今後実装）
│   └── cloudrun/       # Cloud Run（今後実装）
└── environments/        # 環境別設定
    ├── dev/            # 開発環境
    ├── staging/        # ステージング環境（今後実装）
    └── prod/           # 本番環境（今後実装）
```

## 前提条件

- Terraform v1.5.0以上
- Google Cloud SDK（gcloud CLI）
- 有効なGCPプロジェクト
- 必要なAPIの有効化（Terraformが自動的に有効化します）

## セットアップ（開発環境）

1. **開発環境ディレクトリへ移動**
   ```bash
   cd environments/dev
   ```

2. **terraform.tfvarsファイルの作成**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # terraform.tfvarsを編集してproject_idを設定
   ```

3. **Terraformの初期化**
   ```bash
   terraform init
   ```

4. **リソースの作成計画を確認**
   ```bash
   terraform plan
   ```

5. **リソースの作成**
   ```bash
   terraform apply
   ```

## 作成されるリソース

### タスク2.1で必要なリソース（作成済み）
- **Cloud Storage バケット**: `ejan-minimum-storage-{environment}` - アップロードされた画像・動画の保存
- **サービスアカウント**: `ejan-minimum-{environment}-sa`
- **IAM権限**:
  - Storage Admin（バケットレベル）
  - Storage Object Admin（プロジェクトレベル）
  - AI Platform User（Gemini, Nano Banana, Veo3用）

### タスク4.1で必要なリソース（未作成）
- **Cloud Functions**: Veo3動画生成用（functions.tfで定義予定）

### タスク9.2で必要なリソース（未作成）
- **Cloud Run**: APIサーバーのホスティング（cloudrun.tfで定義予定）

## モジュール

### storage モジュール
Cloud Storageバケットを作成・管理します。
- バケット名: `ejan-minimum-storage-{environment}`
- CORS設定、ライフサイクルルール、バージョニング設定が可能

### iam モジュール
サービスアカウントとIAM権限を管理します。
- サービスアカウント: `ejan-minimum-{environment}-sa`
- Storage Admin、AI Platform User等の必要な権限を付与

### functions モジュール（今後実装）
Cloud Functionsリソースを管理します。

### cloudrun モジュール（今後実装）
Cloud Runサービスを管理します。

## 環境別設定

### 開発環境（dev）
- バケット: 30日後に自動削除、バージョニング無効
- force_destroy: true（リソース削除時にデータも削除）

### ステージング環境（staging）- 今後実装
- バケット: バージョニング有効
- force_destroy: false

### 本番環境（prod）- 今後実装
- バケット: バージョニング有効、バックアップ設定
- force_destroy: false
- 削除保護有効

## 出力値の利用

開発環境での例：

```bash
cd environments/dev

# すべての出力値を表示
terraform output

# 特定の値を取得
terraform output storage_bucket_name
terraform output -raw service_account_key | base64 -d > service-account-key.json
```

## 環境変数の設定

アプリケーションの`.env`ファイルに以下を設定：

```bash
cd environments/dev
echo "STORAGE_BUCKET=$(terraform output -raw storage_bucket_name)" >> ../../../apps/api/.env
echo "PROJECT_ID=$(terraform output -raw project_id)" >> ../../../apps/api/.env
```

## クリーンアップ

リソースを削除する場合：

```bash
cd environments/dev
terraform destroy
```

**注意**: 開発環境では`force_destroy = true`が設定されているため、バケット内のデータも含めて削除されます。

## トラブルシューティング

### APIが有効化されていないエラー
Terraformが自動的にAPIを有効化しますが、手動で有効化する場合：
```bash
gcloud services enable storage-api.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 権限エラー
実行ユーザーに以下のロールが必要です：
- Project Editor または Owner
- Service Account Admin
- Storage Admin