# 実装計画

## 実装前の準備

### 重要な実装ルール

⚠️ **必須: 各サブタスク完了時に以下を実行し、エラーが0になるまで修正すること**

1. **コードフォーマット**: 実装したコードを整形
2. **リンター実行**: コード品質チェック - **エラーと警告をすべて解消**
3. **型チェック**: 型安全性の確認 - **any型の使用禁止**
4. **テスト実行**: 関連するテストの実行 - **カバレッジ80%以上**
5. **ドキュメント作成**: `docs/agents/`以下に実装内容を記録

**エラーが残っている状態で次のタスクに進むことは禁止**

### 品質チェックコマンド

```bash
# Python (Backend) - エラーが0になることを確認
cd apps/api
uv run black .                 # フォーマッター（自動修正）
uv run ruff check . --fix      # リンター（自動修正可能な項目）
uv run ruff check .            # リンター（残りのエラー確認）
uv run mypy . --strict         # 型チェック（厳密モード）
uv run pytest tests/ --cov=app --cov-report=term-missing  # テスト実行とカバレッジ

# TypeScript (Frontend) - エラーが0になることを確認
cd apps/web
npm run format                 # Prettierフォーマット（自動修正）
npm run lint -- --fix          # ESLint自動修正
npm run lint                   # ESLintエラー確認
npm run build                  # TypeScriptビルドチェック
npm run test -- --coverage     # テスト実行とカバレッジ（設定時）
```

**成功基準**: すべてのコマンドが Exit Code 0 で終了すること

### 必要なツール・環境
- **Python 3.11+**: Backend開発用
- **Node.js 18+**: Frontend開発用
- **uv**: Pythonパッケージマネージャー（pip/venvではない）
- **gcloud CLI**: Google Cloud Platform管理
- **Google Cloud Project**: 事前に作成済み
- **環境変数**: `.env`ファイルに以下を設定
  ```env
  GOOGLE_API_KEY=<Gemini/Nano Banana/Veo3用のAPIキー>
  GOOGLE_CLOUD_PROJECT=<GCPプロジェクトID>
  STORAGE_BUCKET=<Cloud Storageバケット名>
  ```

### 参考資料の場所
- **サンプル実装**: `apps/api/samples/`
  - `image_generation_with_nano_banana.py`: Nano Banana画像生成の参考
  - `video_generation_with_veo3.py`: Veo3動画生成の参考
- **既存UI実装**: `apps/web/app/`の各ページ（モックデータ使用中）
- **設計書**: `.kiro/specs/ejan-minimum/design.md`
- **要件書**: `.kiro/specs/ejan-minimum/requirements.md`

## 実装タスク一覧

- [ ] 1. バックエンドAPIの基盤構築
- [ ] 1.1 FastAPIプロジェクトの初期セットアップ
  - **作成場所**: `apps/api/app/main.py`
  - **使用ツール**: `uv add fastapi uvicorn python-dotenv`
  - **実装内容**:
    - FastAPIアプリケーションのエントリーポイント作成
    - 環境変数管理とconfigモジュールの実装 (`app/core/config.py`)
    - CORSミドルウェアの設定（localhost:3000を許可）
    - エラーハンドリングミドルウェアの実装
    - ヘルスチェックエンドポイントの追加 (`GET /health`)
  - **参考**: FastAPI公式ドキュメント、`structure.md`のバックエンド構造
  - **実行コマンド**: `cd apps/api && uv run fastapi dev app/main.py`
  - **完了時チェック**:
    ```bash
    uv run black app/
    uv run ruff check app/
    uv run mypy app/
    ```
  - **ドキュメント作成**: `docs/agents/01-fastapi-setup.md`に実装詳細を記録
  - _Requirements: 基盤となる設定（全要件の前提）_

- [ ] 1.2 リクエスト/レスポンスのデータモデル定義
  - **作成場所**: `apps/api/app/models/request.py`, `response.py`
  - **使用ツール**: `uv add pydantic`
  - **実装内容**:
    - 写真アップロード用のリクエストスキーマ作成 (Base64エンコード画像、性別enum)
    - スタイル生成レスポンスのモデル定義 (id, title, description, imageUrl)
    - チュートリアル生成用のリクエスト/レスポンスモデル作成
    - エラーレスポンスの統一フォーマット定義
    - バリデーションルールの実装（ファイルサイズ10MB、JPEG/PNG/WebP）
  - **参考**: `design.md`のデータモデルセクション、Pydanticドキュメント
  - **完了時チェック**:
    ```bash
    uv run black app/models/
    uv run ruff check app/models/
    uv run mypy app/models/
    ```
  - **ドキュメント作成**: `docs/agents/02-data-models.md`にスキーマ定義を記録
  - _Requirements: 1.3, 1.4, 2.1, 6.4_

- [ ] 2. Google Cloud Storageサービスの実装
- [ ] 2.1 Cloud Storage クライアントのセットアップ
  - **作成場所**: `apps/api/app/core/storage.py`
  - **使用ツール**: `uv add google-cloud-storage`
  - **実装内容**:
    - Google Cloud Storage認証設定（サービスアカウントejan-dev-sa使用）
    - バケット接続の確立とテスト
    - サービスアカウント権限の確認
    - 環境変数からのバケット名取得 (`STORAGE_BUCKET`)
  - **参考**: Google Cloud Storage Python Client ドキュメント
  - **テストコマンド**: `gsutil ls gs://$STORAGE_BUCKET`
  - **完了時チェック**:
    ```bash
    uv run black app/core/
    uv run ruff check app/core/
    uv run mypy app/core/
    ```
  - **ドキュメント作成**: `docs/agents/03-storage-setup.md`にGCS設定を記録
  - _Requirements: 5.1, 5.2_

- [ ] 2.2 ファイルアップロード・管理機能の実装
  - **作成場所**: `apps/api/app/services/storage.py`
  - **実装内容**:
    - ユニークファイル名生成ロジック（UUID + タイムスタンプ）
    - 画像アップロード処理（JPEG、PNG、WebP対応）
    - 動画アップロード処理（MP4形式）
    - 公開URL生成メカニズム
    - アップロード失敗時のリトライ処理（指数バックオフ）
  - **参考**: `design.md`のCloudStorageServiceセクション
  - **公開URL形式**: `https://storage.googleapis.com/{bucket}/{file_path}`
  - **完了時チェック**:
    ```bash
    uv run black app/services/
    uv run ruff check app/services/
    uv run mypy app/services/
    uv run pytest tests/unit/test_storage.py  # テスト作成後
    ```
  - **ドキュメント作成**: `docs/agents/03-storage-setup.md`に実装詳細を追記
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 3. AI統合サービスの実装
- [ ] 3.1 Gemini API統合基盤の構築
  - **作成場所**: `apps/api/app/services/ai_client.py`
  - **使用ツール**: `uv add google-genai pillow`
  - **実装内容**:
    - google-genaiライブラリのセットアップ
    - APIキー管理と認証設定 (`GOOGLE_API_KEY`)
    - Gemini クライアントの初期化
    - エラーハンドリングとリトライロジック（3回まで）
  - **参考**: `apps/api/samples/`の既存サンプル、Google AI Python SDK
  - **モデル名**: `gemini-2.5-flash`, `gemini-2.5-flash-image-preview`
  - **完了時チェック**:
    ```bash
    uv run black app/services/
    uv run ruff check app/services/
    uv run mypy app/services/
    ```
  - **ドキュメント作成**: `docs/agents/04-ai-integration.md`にAPI設定を記録
  - _Requirements: 3.1_

- [ ] 3.2 Nano Banana画像生成サービスの実装
  - **作成場所**: `apps/api/app/services/image_generation.py`
  - **実装内容**:
    - スタイル生成用プロンプトテンプレート作成
    - 性別別のプロンプトバリエーション定義（男性/女性/中性）
    - 3パターンのスタイル画像生成ロジック
    - 生成画像のCloud Storage保存処理
    - カスタマイズテキストのプロンプト反映
  - **参考**: `samples/image_generation_with_nano_banana.py`
  - **プロンプト例**: "Professional makeup style for {gender} face photo..."
  - **コスト**: $0.039/画像 × 3 = $0.117/リクエスト
  - _Requirements: 1.5, 1.7, 2.4, 3.2_

- [ ] 3.3 Gemini Structured Outputによる手順構造化
  - **作成場所**: `apps/api/app/services/tutorial_structure.py`
  - **実装内容**:
    - メイクアップ手順のデータ構造定義（Pydanticモデル: MakeupProcedure）
    - 構造化出力のリクエスト実装 (`response_mime_type: "application/json"`)
    - タイトル、説明、ステップ、道具リストの抽出
    - JSONスキーマによるレスポンス検証
    - エラー時のフォールバック処理
  - **参考**: Gemini Structured Output API ドキュメント
  - **response_schema例**: `list[MakeupStep]`形式
  - _Requirements: 3.1, 3.2_

- [ ] 4. Cloud Function動画生成サービスの実装
- [ ] 4.1 Veo3動画生成Functionの作成
  - **作成場所**: `apps/functions/video_generation/main.py`
  - **実装内容**:
    - Cloud Functionエントリーポイントの実装 (`def generate_video(request)`)
    - 画像URLとプロンプトの受信処理
    - Veo3 APIの呼び出しロジック (`model="veo-3.0-generate-001"`)
    - Operation IDの取得と管理
    - requirements.txtとデプロイ設定の作成
  - **参考**: `samples/video_generation_with_veo3.py`
  - **デプロイ**: `gcloud functions deploy generate_video --runtime python311`
  - _Requirements: 3.4, 3.5_

- [ ] 4.2 ポーリングとStorage保存処理の実装
  - **作成場所**: 同上 (`apps/functions/video_generation/main.py`)
  - **実装内容**:
    - 10秒間隔のステータスポーリングロジック (`time.sleep(10)`)
    - 生成完了の検知処理 (`operation.done`チェック)
    - 動画データのCloud Storage直接保存
    - 保存URL返却処理
    - タイムアウト処理（最大540秒 = Cloud Functions制限）
    - エラーハンドリングと失敗時のレスポンス
  - **参考**: `samples/video_generation_with_veo3.py`のポーリング部分
  - **動画形式**: MP4、10秒間の動画
  - **コスト**: $0.75/秒 × 10秒 = $7.50/動画
  - _Requirements: 3.5, 3.6, 5.1_

- [ ] 5. バックエンドAPIエンドポイントの実装
- [ ] 5.1 スタイル生成エンドポイントの構築
  - **作成場所**: `apps/api/app/api/routes/styles.py`
  - **実装内容**:
    - POST /api/styles/generateの実装
    - 写真受信とバリデーション処理（Base64デコード、サイズチェック）
    - Nano Banana呼び出しとレスポンス生成
    - 非同期処理によるパフォーマンス最適化 (`async def`)
    - エラーレスポンスの適切な返却
  - **リクエスト形式**: `{"photo": "base64...", "gender": "male|female|neutral"}`
  - **レスポンス形式**: `{"styles": [{id, title, description, imageUrl}]}`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [ ] 5.2 チュートリアル生成エンドポイントの構築
  - **作成場所**: `apps/api/app/api/routes/tutorials.py`
  - **実装内容**:
    - POST /api/tutorials/generateの実装
    - スタイルIDとカスタマイズテキストの処理
    - Gemini構造化→画像生成→動画生成の順次処理
    - Cloud Function呼び出しロジック（HTTPリクエスト）
    - チュートリアルデータの組み立て
  - **処理時間**: 約3-4分（動画生成含む）
  - **Cloud Function URL**: 環境変数で管理
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 5.3 スタイル詳細取得エンドポイントの実装
  - **作成場所**: `apps/api/app/api/routes/styles.py`
  - **実装内容**:
    - GET /api/styles/{id}の実装
    - スタイル情報のメモリまたはキャッシュ管理（シンプルなdict保存）
    - 必要な道具リストと説明の返却
    - 404エラー処理
  - **キャッシュ**: デモ環境のため、メモリ内辞書で管理
  - _Requirements: 2.1, 2.2_

- [ ] 6. フロントエンド・バックエンド統合
- [ ] 6.1 API通信レイヤーの実装
  - **作成場所**: `apps/web/lib/api/client.ts`
  - **実装内容**:
    - フロントエンドのAPIクライアント作成
    - 環境変数によるAPIエンドポイント設定 (`NEXT_PUBLIC_API_URL`)
    - fetch APIラッパーの実装
    - リクエスト/レスポンスの型定義 (`types/api.ts`)
    - エラーハンドリングとリトライロジック
  - **環境変数**: `apps/web/.env.local`に`NEXT_PUBLIC_API_URL=http://localhost:8000`
  - **参考**: Next.js fetch APIドキュメント
  - **完了時チェック**:
    ```bash
    cd apps/web
    npm run format
    npm run lint
    npm run build
    ```
  - **ドキュメント作成**: `docs/agents/07-frontend-integration.md`にAPI統合方法を記録
  - _Requirements: 基盤となる通信設定_

- [ ] 6.2 写真アップロード画面とAPI連携
  - **修正場所**: `apps/web/app/page.tsx`, `components/photo-upload.tsx`
  - **実装内容**:
    - モックデータをAPI呼び出しに置き換え
    - ファイルアップロードのBase64エンコード処理
    - アップロード中のローディング表示実装（既存のProgressコンポーネント使用）
    - エラー時のトースト通知実装（sonner使用）
    - レスポンス受信後の画面遷移処理（`useRouter`）
  - **既存コンポーネント**: shadcn/uiのProgress、Toast
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 6.1, 6.2, 6.5_

- [ ] 6.3 スタイル選択画面のAPI統合
  - **修正場所**: `apps/web/app/styles/page.tsx`
  - **実装内容**:
    - 生成されたスタイルの動的表示
    - Cloud Storage画像URLの表示処理（Next.js Imageコンポーネント）
    - スタイル選択時のAPI呼び出し
    - カスタマイズテキストの送信処理
  - **State管理**: React useState、useSearchParams
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 6.4 チュートリアル生成・表示画面の統合
  - **修正場所**: `apps/web/app/generating/page.tsx`, `apps/web/app/tutorial/page.tsx`
  - **実装内容**:
    - チュートリアル生成APIの呼び出し
    - 生成中の進捗表示（約3分の待機時間表示）
    - 動画URLの受信と再生処理（HTML5 video要素）
    - ステップごとの画像・動画表示
    - 前後ステップナビゲーション機能
  - **既存コンポーネント**: Tabs、AspectRatio、Card
  - _Requirements: 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 6.3_

- [ ] 7. エラーハンドリングとユーザビリティの実装
- [ ] 7.1 包括的なエラー処理システムの構築
  - **実装場所**: `apps/web/lib/api/error-handler.ts`、各ページコンポーネント
  - **実装内容**:
    - API呼び出し失敗時の自動リトライ（最大3回、指数バックオフ）
    - ネットワークエラーの検知と通知
    - サポート外フォーマットのメッセージ表示
    - プログレスバー/スピナーコンポーネントの実装
    - エラーメッセージのローカライズ（日本語対応）
  - **使用コンポーネント**: Toast (sonner)、AlertDialog、Progress
  - **エラー種別**: ネットワーク、タイムアウト、バリデーション、サーバーエラー
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7.2 UI/UX最適化とデスクトップ表示
  - **修正場所**: 各ページのレイアウトとスタイル
  - **実装内容**:
    - デスクトップ解像度での適切なレイアウト調整（max-width: 1200px）
    - クリック可能要素の明確な視覚化（hover効果、cursor: pointer）
    - 画像・動画の適切なサイズ調整（AspectRatio使用）
    - 最小幅制限とスクロールバー処理（min-width: 1024px）
    - ローディング状態の視覚的フィードバック（Skeleton、Spinner）
  - **Tailwind classes**: `container mx-auto`, `max-w-7xl`, `hover:scale-105`
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8. テストの実装
- [ ] 8.1 バックエンドユニットテストの作成
  - **作成場所**: `apps/api/tests/unit/`
  - **使用ツール**: `uv add --dev pytest pytest-asyncio pytest-mock`
  - **テスト内容**:
    - CloudStorageServiceのテスト（アップロード、URL生成）
    - StyleGenerationServiceのテスト（プロンプト生成）
    - TutorialGenerationServiceのテスト（構造化処理）
    - バリデーションロジックのテスト（サイズ、フォーマット）
    - エラーハンドリングのテスト
  - **実行コマンド**: `cd apps/api && uv run pytest tests/unit/`
  - **完了時チェック**:
    ```bash
    uv run black tests/
    uv run ruff check tests/
    uv run pytest tests/unit/ -v
    ```
  - **ドキュメント作成**: `docs/agents/09-testing-strategy.md`にテスト戦略を記録
  - _Requirements: 品質保証のため_

- [ ] 8.2 API統合テストの実装
  - **作成場所**: `apps/api/tests/integration/`
  - **使用ツール**: `uv add --dev httpx`
  - **テスト内容**:
    - スタイル生成エンドポイントのテスト
    - チュートリアル生成エンドポイントのテスト
    - エラーレスポンスの検証
    - Cloud Function呼び出しのモックテスト
  - **モック**: AI APIとCloud Functionをモック化
  - **実行コマンド**: `cd apps/api && uv run pytest tests/integration/`
  - _Requirements: 品質保証のため_

- [ ] 8.3 フロントエンドE2Eテストの作成
  - **作成場所**: `apps/web/tests/e2e/`
  - **使用ツール**: `npm install --save-dev @playwright/test`
  - **テスト内容**:
    - 写真アップロードからスタイル選択までのフロー
    - スタイル選択からチュートリアル表示までのフロー
    - エラー発生時の適切な表示確認
    - ローディング状態の動作確認
  - **実行コマンド**: `cd apps/web && npm run test:e2e`
  - **CI考慮**: GitHub Actionsでの自動実行も想定
  - _Requirements: 全要件の動作確認_

- [ ] 9. 最終統合と動作確認
- [ ] 9.1 全体システムの結合テスト
  - **テスト環境**: ローカル開発環境
  - **テスト内容**:
    - エンドツーエンドの完全なユーザーフロー確認
    - 各コンポーネント間の連携確認
    - パフォーマンスのベースライン測定（応答時間記録）
    - メモリリークや接続リークの確認
  - **確認項目**:
    - 写真アップロード→スタイル生成（約30秒）
    - チュートリアル生成（約3-4分）
    - 動画再生の動作確認
  - **ツール**: Chrome DevTools（Network、Performance、Memory）
  - _Requirements: 全要件_

- [ ] 9.2 デモ環境での最終調整
  - **チェックリスト**:
    - 環境変数の本番設定確認（`.env`、`.env.local`）
    - Cloud Storageアクセス権限の検証（gsutilコマンド）
    - APIキーとサービスアカウントの動作確認
    - エラーログの収集と分析
    - システム全体の安定性確認
  - **本番環境変数例**:
    ```
    GOOGLE_API_KEY=実際のAPIキー
    GOOGLE_CLOUD_PROJECT=ejan-demo-project
    STORAGE_BUCKET=ejan-demo-storage
    FUNCTION_URL=https://us-central1-ejan-demo.cloudfunctions.net/generate_video
    ```
  - **デプロイコマンド**:
    - Backend: `gcloud run deploy ejan-api --source .`
    - Frontend: `vercel deploy`
  - **完了時チェック**:
    ```bash
    # 全体的な品質チェック
    cd apps/api && uv run black . && uv run ruff check . && uv run mypy .
    cd apps/web && npm run format && npm run lint && npm run build
    ```
  - **ドキュメント作成**: `docs/agents/10-deployment.md`にデプロイ手順と設定を記録
  - _Requirements: 5.5, 全体的な品質保証_

## 実装優先順位

1. **基盤構築** (タスク1-2): バックエンドとStorageの基礎
2. **AI統合** (タスク3-4): コア機能の実装
3. **API実装** (タスク5): エンドポイントの構築
4. **フロントエンド統合** (タスク6): UIとの接続
5. **品質向上** (タスク7-9): エラー処理とテスト

## 推定実装時間

- 基盤構築: 4-6時間
- AI統合: 6-8時間
- API実装: 4-6時間
- フロントエンド統合: 6-8時間
- 品質向上: 6-8時間

**合計推定時間**: 26-36時間

## ドキュメント構造

### docs/agents/ ディレクトリ構成

```
docs/agents/
├── 01-fastapi-setup.md         # FastAPI初期設定の詳細
├── 02-data-models.md           # Pydanticモデル定義
├── 03-storage-setup.md         # Cloud Storage設定
├── 04-ai-integration.md        # AI API統合方法
├── 05-cloud-functions.md       # Cloud Functions実装
├── 06-api-endpoints.md         # APIエンドポイント仕様
├── 07-frontend-integration.md  # フロントエンド統合
├── 08-error-handling.md        # エラーハンドリング実装
├── 09-testing-strategy.md      # テスト戦略と実装
├── 10-deployment.md            # デプロイ手順
└── README.md                   # ドキュメント一覧と概要
```

### ドキュメント記載内容

各ドキュメントには以下を含める：
1. **概要**: 実装した機能の説明
2. **実装詳細**: 具体的なコード構造
3. **設定項目**: 環境変数や設定ファイル
4. **エラー対処**: 遭遇した問題と解決方法
5. **テスト結果**: 実行したテストと結果
6. **改善点**: 今後の改善提案

## トラブルシューティングガイド

### よくある問題と解決方法

**CORS エラー**
- 原因: FastAPIのCORS設定が不適切
- 解決: `allow_origins=["http://localhost:3000"]`を確認

**画像アップロードエラー**
- 原因: Base64エンコードサイズが10MB超過
- 解決: クライアント側でリサイズ処理を追加

**Veo3タイムアウト**
- 原因: 動画生成が540秒を超過
- 解決: Cloud Functionのタイムアウト設定を確認

**Storage権限エラー**
- 原因: サービスアカウントの権限不足
- 解決: `Storage Object Admin`ロールを付与

### デバッグコマンド

```bash
# バックエンド起動
cd apps/api && uv run fastapi dev app/main.py --reload

# フロントエンド起動
cd apps/web && npm run dev

# ログ確認
gcloud functions logs read generate_video --limit 50

# Storage確認
gsutil ls -la gs://${STORAGE_BUCKET}/
```