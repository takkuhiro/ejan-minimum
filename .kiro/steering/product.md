# Product Overview Steering Document

## Product Overview

**Ejan** (いーじゃん) は、ユーザーの顔写真に最適なメイクアップスタイル（ヘアスタイル＋メイク）を提案し、そのスタイルに到達するための詳細な手順を動画付きチュートリアルで提供するWebアプリケーションです。AIを活用して個人に最適化されたビューティー提案を行います。

## Core Features

- **パーソナライズされたスタイル提案**: ユーザーの顔写真から3パターンのメイクアップスタイルを自動生成
- **段階的チュートリアル**: 各ステップごとの動画と画像による詳細な手順説明
- **カスタマイゼーション**: 提案されたスタイルの微調整やゼロからのスタイル作成
- **性別対応**: 男性、女性、中性的な選択肢に対応したスタイル提案
- **リアルタイム生成**: AI（Nano Banana、Veo3）による画像・動画の動的生成

## Target Use Case

### Primary Use Cases
- **初心者向け変身サポート**: メイクや髪型セットの経験がない人への段階的ガイダンス
- **スタイルの多様化**: 同じメイクに飽きた人への新しい選択肢提供
- **ビジュアル学習**: 文章ではなく動画で学びたい人への実践的チュートリアル

### User Flow Scenario
1. 性別選択と顔写真アップロード（最大10MB）
2. AIが3パターンのおすすめスタイルを自動生成
   - Nano Bananaで画像生成 + メイクアップ手順作成
   - Gemini Structured Outputで手順を構造化（タイトル、説明、番号付きステップ、必要な道具）
3. 好みのスタイルを選択またはカスタマイズ
4. 詳細な手順（動画＋画像）の自動生成（約3分）
   - ステップごとの完成イメージ画像生成
   - ステップ解説動画生成（Veo3）
5. ステップバイステップのチュートリアル閲覧

## Key Value Proposition

### Unique Benefits
- **完全個別対応**: ユーザーの顔に合わせた具体的な提案
- **ビジュアル重視**: テキストではなく画像・動画で直感的に理解
- **段階的学習**: 初心者でも迷わない細かいステップ分割
- **即座の結果確認**: 各ステップの完成イメージを事前に確認可能

### Differentiators
- **AIによる自動生成**: 手動作成ではなくAIが個別に生成
- **動画チュートリアル**: 静止画だけでなく動きのある説明
- **カスタマイズ性**: プリセットだけでなく自由な調整が可能
- **男女両対応**: 女性向けだけでなく男性にも特化した提案

## Product Constraints (Demo Version)

### Out of Scope
- ログイン・認証機能なし
- お気に入り保存機能なし
- レート制限・キューイング処理なし
- ユーザー履歴管理なし
- 課金・決済機能なし

### Performance Expectations
- 画像生成: 数秒〜数十秒
- 動画生成: 約3分（ポーリング含む）
- 同時実行数: 限定的（デモ用）

## Implementation Status

### Completed Components
- **Frontend Mock**: apps/web with all screens using mock data
- **Sample AI Integrations**: Working examples for Nano Banana and Veo3
- **Backend API Structure**: FastAPI application with core setup
- **Storage Service**: Google Cloud Storage integration
- **Data Models**: Request/response schemas defined
- **AI Client Service**: Gemini integration for image/video generation
- **Image Generation Service**: Nano Banana implementation
- **Tutorial Structure Service**: Step-by-step tutorial generation
- **Testing Framework**: Unit and integration test structure with full coverage
- **Infrastructure Modules**: Terraform for storage and IAM

### In Progress
- **API Endpoints**: Finalizing style generation and tutorial endpoints
- **Cloud Functions**: Deploying AI models as serverless functions
- **Frontend-Backend Integration**: Connecting UI to API
- **Cloud Run Deployment**: Container deployment setup

## Business Model (Future)

### Monetization Strategy (Not Implemented)
- Freemium: 基本機能無料、高度なカスタマイズ有料
- 広告モデル: 化粧品ブランドとのタイアップ
- サブスクリプション: 月額での無制限利用

### Success Metrics (Not Tracked)
- アップロード数
- スタイル選択率
- チュートリアル完了率
- カスタマイズ利用率