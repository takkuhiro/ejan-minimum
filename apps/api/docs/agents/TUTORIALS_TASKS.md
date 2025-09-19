# チュートリアル生成API実装タスクリスト

## 概要
このドキュメントは、チュートリアル生成APIの実装に必要な全タスクを詳細に記載したものです。

## タスク一覧

### 1. リクエストモデルの拡張

#### 1.1 TutorialGenerationRequestの修正
**ファイル**: `apps/api/app/models/request.py`
- [ ] `raw_description`フィールドを追加（エイリアス: `rawDescription`）
- [ ] `original_image_url`フィールドを追加（エイリアス: `originalImageUrl`）
- [ ] バリデーションの追加
  - raw_descriptionの最大文字数制限（5000文字）
  - original_image_urlのURL形式検証

### 2. チュートリアル生成サービスの実装

#### 2.1 tutorial_generation.pyの改修
**ファイル**: `apps/api/app/services/tutorial_generation.py`
- [ ] `generate_tutorial`メソッドを実装
  - [ ] rawDescriptionからgemini-2.0-flash-liteでステップ構造生成
  - [ ] 各ステップの画像生成を順次実行
  - [ ] asyncio.create_taskによる並列処理を実装
  - [ ] 各ステップの動画生成を非同期で実行
- [ ] `_generate_step_image_with_previous`メソッドを新規作成
  - [ ] 前ステップ画像 + title + descriptionから完成イメージ生成
  - [ ] 初回はオリジナル画像を使用
- [ ] `_generate_step_video_async`メソッドを実装
  - [ ] 前ステップ画像と指示テキストから動画生成
  - [ ] 非同期でCloud Functionsを呼び出し
- [ ] チュートリアルデータをストレージに保存
  - [ ] メタデータ（JSON）の保存

### 3. Cloud Functions連携の改修

#### 3.1 cloud_function_client.pyの拡張
**ファイル**: `apps/api/app/services/cloud_function_client.py`
- [x] `generate_video`メソッドに`target_gcs_path`パラメータ追加（実装済み）
- [ ] レスポンス処理の改修

#### 3.2 Cloud Functions側の改修
**ファイル**: `apps/functions/video_generation/main.py`
- [x] リクエストから`target_gcs_path`を取得（実装済み）
- [x] 指定されたGCSパスに動画を保存（実装済み）

### 4. ステータス確認APIの実装

#### 4.1 新規エンドポイントの追加
**ファイル**: `apps/api/app/api/routes/tutorials.py`
- [ ] `/api/tutorials/{tutorialId}/status`エンドポイントを追加
- [ ] レスポンスモデルの作成
  - [ ] 全体の進捗率
  - [ ] 各ステップの状態（pending/processing/completed）
  - [ ] 完成した動画のURL一覧

#### 4.2 ステータス確認ロジックの実装
**ファイル**: `apps/api/app/services/tutorial_generation.py`
- [ ] `check_tutorial_status`メソッドを新規作成
- [ ] GCS上の動画ファイル存在確認
- [ ] 進捗率の計算ロジック

### 5. ストレージサービスの拡張

#### 5.1 storage.pyの機能追加
**ファイル**: `apps/api/app/services/storage.py`
- [ ] `file_exists`メソッドの活用（既に実装済み）
- [ ] `list_files_with_prefix`メソッドの追加（必要に応じて）
- [ ] チュートリアルメタデータの保存・取得メソッド

### 6. レスポンスモデルの追加

#### 6.1 response.pyの拡張
**ファイル**: `apps/api/app/models/response.py`
- [ ] `TutorialStatusResponse`モデルの作成
- [ ] `StepStatus`enumの定義（pending/processing/completed）
- [ ] バリデーションルールの追加

### 7. 画像生成サービスの拡張

#### 7.1 image_generation.pyの改修
**ファイル**: `apps/api/app/services/image_generation.py`
- [ ] `generate_step_image`メソッドの新規作成
  - [ ] 前画像 + テキストプロンプトから生成
  - [ ] gemini-2.5-flash-image-previewの使用
- [ ] エラーハンドリングの強化
- [ ] リトライロジックの実装

### 8. 非同期処理の実装

#### 8.1 並列処理フロー
- [ ] 各ステップごとに非同期タスクを生成
- [ ] asyncio.create_taskで並列実行
- [ ] エラーハンドリングの実装

### 9. 統合とテスト

#### 9.1 エラーハンドリング
- [ ] 各ステップでのエラー処理
- [ ] 部分的な失敗時の対応
- [ ] タイムアウト処理

#### 9.2 ログの実装
- [ ] 各ステップの開始・終了ログ
- [ ] エラーログの詳細化
- [ ] パフォーマンスメトリクスの記録

#### 9.3 テストの実装
- [ ] ユニットテストの作成
- [ ] 統合テストの作成
- [ ] エンドツーエンドテストの実施

## 実装順序

1. **Phase 1: 基盤整備**
   - リクエストモデルの拡張
   - レスポンスモデルの追加

2. **Phase 2: コア機能実装**
   - チュートリアル生成サービスの改修
   - 画像生成サービスの拡張
   - 非同期動画生成の実装

3. **Phase 3: ステータス管理**
   - ステータス確認APIの実装
   - ストレージサービスの拡張

4. **Phase 4: 品質向上**
   - エラーハンドリングの実装
   - ログの充実
   - テストの作成と実行

## 注意事項

- 各ステップの画像生成では、必ず前ステップの完成画像を入力として使用する
- 動画生成は各ステップごとに非同期で並列処理
- GCSのパスは`tutorials/{tutorialId}/step_{stepNumber}/`の形式で統一
- エラー発生時も部分的な成功結果は保持する

## 成功基準

- [ ] rawDescriptionから完全なチュートリアルが生成される
- [ ] 各ステップの画像が前ステップを反映している
- [ ] 動画生成が非同期で並列処理される
- [ ] 動画生成の進捗がリアルタイムで確認できる
- [ ] エラー時も適切なリカバリーが可能