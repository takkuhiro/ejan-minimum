# Claude Code Spec-Driven Development

Kiro-style Spec Driven Development implementation using claude code slash commands, hooks and agents.

## Project Context

### Paths
- Steering: `.kiro/steering/`
- Specs: `.kiro/specs/`
- Commands: `.claude/commands/`

### Steering vs Specification

**Steering** (`.kiro/steering/`) - Guide AI with project-wide rules and context
**Specs** (`.kiro/specs/`) - Formalize development process for individual features

### Active Specifications
- Check `.kiro/specs/` for active specifications
- Use `/kiro:spec-status [feature-name]` to check progress

## Development Guidelines
- Think in English, but generate responses in Japanese (思考は英語、回答の生成は日本語で行うように)

## Workflow

### Phase 0: Steering (Optional)
`/kiro:steering` - Create/update steering documents
`/kiro:steering-custom` - Create custom steering for specialized contexts

Note: Optional for new features or small additions. You can proceed directly to spec-init.

### Phase 1: Specification Creation
1. `/kiro:spec-init [detailed description]` - Initialize spec with detailed project description
2. `/kiro:spec-requirements [feature]` - Generate requirements document
3. `/kiro:spec-design [feature]` - Interactive: "Have you reviewed requirements.md? [y/N]"
4. `/kiro:spec-tasks [feature]` - Interactive: Confirms both requirements and design review

### Phase 2: Progress Tracking
`/kiro:spec-status [feature]` - Check current progress and phases

## Development Rules
1. **Consider steering**: Run `/kiro:steering` before major development (optional for new features)
2. **Follow 3-phase approval workflow**: Requirements → Design → Tasks → Implementation
3. **Approval required**: Each phase requires human review (interactive prompt or manual)
4. **No skipping phases**: Design requires approved requirements; Tasks require approved design
5. **Update task status**: Mark tasks as completed when working on them
6. **Keep steering current**: Run `/kiro:steering` after significant changes
7. **Check spec compliance**: Use `/kiro:spec-status` to verify alignment

## Steering Configuration

### Current Steering Files
Managed by `/kiro:steering` command. Updates here reflect command changes.

### Active Steering Files
- `product.md`: Always included - Product context and business objectives
- `tech.md`: Always included - Technology stack and architectural decisions
- `structure.md`: Always included - File organization and code patterns

### Custom Steering Files
<!-- Added by /kiro:steering-custom command -->
<!-- Format:
- `filename.md`: Mode - Pattern(s) - Description
  Mode: Always|Conditional|Manual
  Pattern: File patterns for Conditional mode
-->

### Inclusion Modes
- **Always**: Loaded in every interaction (default)
- **Conditional**: Loaded for specific file patterns (e.g., "*.test.js")
- **Manual**: Reference with `@filename.md` syntax


### 必須ルール (MUST FOLLOW)
1. **Git操作の使い分け**
   - Git管理下のファイル移動: `git mv` を使用
   - Git管理下のファイル削除: `git rm` を使用
   - 未追跡ファイル（新規作成等）: 通常の `rm`, `mv` を使用可

2. **Terraform実行**
   - Terraformコマンドの実行はユーザーに委ねる
   - 設定ファイルの作成・編集のみ行う
   - `terraform plan/apply/destroy` は実行しない

3. **テストファイルの整理**
   - TDDのテストファイルは専用ディレクトリに配置
   - 例: `tests/unit/`, `tests/integration/`, `tests/e2e/`
   - ルートディレクトリの散乱を防ぐ

4. **ファイル末尾は改行で終える**
   - git管理しているため、ファイル末尾は改行で終える

5. **Pythonコード品質チェック**
   - Pythonファイルの追加・編集後は必ず以下を実行:
     - `black`: コードフォーマッター
     - `ruff`: リンター
     - `mypy`: 型チェッカー
   - 型安全性を保つため、型ヒントを積極的に使用
   - pyproject.tomlの設定を使用して正しく実行 (e.g. cd apps/api & uv run mypy .)

6. **TypeScript/JavaScriptコード品質チェック**
   - TypeScript/JavaScriptファイルの追加・編集後は必ず以下を実行:
     - `npm run format`: Prettierによるコードフォーマット
     - `npm run lint`: ESLintによるリンティング
     - `npm run build`: TypeScriptコンパイルとビルドチェック
   - apps/webディレクトリで実行 (e.g. cd apps/web && npm run format && npm run lint && npm run build)
   - 型安全性を保つため、any型の使用を避け、適切な型定義を行う

7. **機能実装後のテスト実行（必須）**
   - **重要**: 機能実装が完了したら、必ず関連するすべてのテストを実行し、合格することを確認する
   - **Pythonプロジェクト（apps/api）**:
     - `uv run pytest`: すべてのテストを実行
     - `uv run pytest tests/unit/`: ユニットテストのみ実行
     - `uv run pytest tests/integration/`: 統合テストのみ実行
     - `uv run pytest -v`: 詳細な出力でテスト実行
   - **TypeScript/JavaScriptプロジェクト（apps/web）**:
     - `npm run test`: すべてのテストを実行
     - `npm run test:unit`: ユニットテストのみ実行
     - `npm run test:integration`: 統合テストのみ実行（設定されている場合）
     - `npm run test:watch`: ファイル変更を監視してテストを自動実行
   - **テスト失敗時の対応**:
     - テストが失敗した場合は、必ず修正してから作業を完了とする
     - 既存のテストが失敗する場合は、実装を見直す（テストの変更は慎重に）
     - 新機能の場合は、対応するテストも必ず追加する

### プロジェクト固有の設定
- **アプリケーション構造**: `apps/{web,api}` (frontendやbackendではない)
- **Python環境**: uvを使用（pip/venvではなく）
- **データ管理**: 検証環境のため、画像・動画データは削除せずCloud Storageに保存
- **サービスアカウント**: 開発環境では単一のサービスアカウント`ejan-dev-sa`を使用
  - Google Cloud リソース（Storage, SQL）とFirebase認証の両方に使用
  - 本番環境では用途別に分離予定

### Next.jsプロジェクト構造 (apps/web)
**重要**: srcディレクトリは使用しません。以下の構造を厳守してください。

```
apps/web/
├── app/              # App Router - ルーティングとページコンポーネントのみ
│   ├── layout.tsx    # ルートレイアウト
│   ├── page.tsx      # ホームページ
│   ├── globals.css   # グローバルスタイル
│   └── [route]/      # 各ルートディレクトリ
│       └── page.tsx  # ページコンポーネント
├── components/       # すべての再利用可能なコンポーネント
│   ├── ui/          # shadcn/ui コンポーネント
│   ├── layout/      # レイアウトコンポーネント（Header, Footer等）
│   ├── tutorial/    # チュートリアル関連コンポーネント
│   └── [feature]/   # 機能別コンポーネント
├── lib/             # ユーティリティとライブラリ関数
│   ├── api/         # API関連
│   ├── auth/        # 認証関連
│   └── utils.ts     # 共通ユーティリティ
├── hooks/           # カスタムReactフック
├── stores/          # 状態管理（Jotai）
├── types/           # TypeScript型定義
└── public/          # 静的ファイル

**禁止事項**:
- srcディレクトリの作成・使用
- app内へのコンポーネント配置（page.tsx以外）
- __tests__ディレクトリの使用（testsを使用）

**パスエイリアス**:
- `@/*` はプロジェクトルート（apps/web/）を指す
- 例: `@/components/ui/button` → `apps/web/components/ui/button`
