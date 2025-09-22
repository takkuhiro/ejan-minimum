# EJAN Minimum

![](apps/web/public/logo_transparent.png)

AIメイクアップガイド Ejanの最小実装版です。


## 機能

- AIを活用した画像生成
- スタイル転送による画像カスタマイズ
- チュートリアルガイド付きの直感的なUI

## 技術スタック

### フロントエンド (apps/web)
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Jotai (状態管理)

### バックエンド (apps/api)
- FastAPI
- Python 3.11+
- uv (パッケージ管理)

### インフラ
- Google Cloud Storage
- Cloud Run
- Cloud Run Functions

## セットアップ

### 前提条件
- Node.js 18+
- Python 3.11+
- uv
- Google Cloud SDK

### インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd ejan-minimum

# フロントエンドの依存関係をインストール
cd apps/web
npm install

# バックエンドの依存関係をインストール
cd ../api
uv sync
```

### 環境変数

各アプリケーションディレクトリに `.env.local` を作成：

#### apps/web/.env.local
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

#### apps/api/.env
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCS_BUCKET_NAME=your-bucket-name
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 開発

```bash
# フロントエンド開発サーバー
cd apps/web
npm run dev

# バックエンド開発サーバー
cd apps/api
uv run uvicorn main:app --reload
```

## テスト

```bash
# フロントエンドテスト
cd apps/web
npm run test

# バックエンドテスト
cd apps/api
uv run pytest
```

## ビルド

```bash
# フロントエンドビルド
cd apps/web
npm run build

# バックエンドは直接実行
cd apps/api
uv run uvicorn main:app
```
