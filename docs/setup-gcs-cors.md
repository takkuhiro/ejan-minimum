# Google Cloud Storage CORS Setup

## 概要
ブラウザからGoogle Cloud Storageの画像を直接取得するためのCORS設定手順。

## 設定手順

### 1. CORS設定の適用
プロジェクトルートで以下のコマンドを実行：

```bash
# 開発環境のバケット
gsutil cors set cors-config.json gs://ejan-minimum-dev

# 本番環境のバケット（必要に応じて）
# gsutil cors set cors-config.json gs://ejan-minimum-prod
```

### 2. 設定の確認
```bash
gsutil cors get gs://ejan-minimum-dev
```

### 3. 設定の削除（必要な場合）
```bash
gsutil cors set /dev/null gs://ejan-minimum-dev
```

## CORS設定内容

- **許可オリジン**:
  - `http://localhost:3000` (Next.js開発サーバー)
  - `http://localhost:8000` (FastAPI開発サーバー)
  - `https://*.vercel.app` (Vercelデプロイメント)

- **許可メソッド**: GET, HEAD
- **レスポンスヘッダー**: Content-Type
- **キャッシュ時間**: 3600秒（1時間）

## トラブルシューティング

### 画像が読み込めない場合

1. ブラウザの開発者ツールでネットワークタブを確認
2. CORSエラーが表示されている場合は、以下を確認：
   - バケットのCORS設定が正しく適用されているか
   - 画像URLが正しいか
   - 画像がpublicに設定されているか

### 権限エラーの場合

```bash
# サービスアカウントの権限を確認
gcloud projects get-iam-policy ejan-minimum

# 必要に応じて権限を付与
gcloud projects add-iam-policy-binding ejan-minimum \
  --member="serviceAccount:ejan-minimum-dev-sa@ejan-minimum.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

## 関連ファイル
- `/cors-config.json` - CORS設定ファイル
- `/apps/api/app/services/storage.py` - 画像アップロード実装
- `/apps/web/app/styles/page.tsx` - 画像表示実装