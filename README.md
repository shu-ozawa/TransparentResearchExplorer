# Transparent Research Explorer (TRE) プロトタイプ

## 1. プロジェクト概要

Transparent Research Explorer (TRE) は、arXiv から論文を検索し、検索プロセスとその結果を可視化することで、研究者の先行研究調査を支援するシステムのプロトタイプです。検索クエリの枝分かれ・進化の透明化と、論文選択プロセスの可視化を中心に据え、「AIが何をどのように検索したか」を明示することを目的としています。

## 2. 技術スタック

### バックエンド
- **言語/フレームワーク:** Python + FastAPI
- **AI API:** Google Gemini API
- **外部API:** arXiv API
- **データベース:** SQLite（プロトタイプ用軽量DB）
- **文書処理:** NLTK, spaCy (基本的なテキスト処理)

### フロントエンド
- **フレームワーク:** React.js
- **UI ライブラリ:** Material-UI または Chakra UI (プロジェクト初期設定で選択)
- **可視化ライブラリ:** D3.js（クエリツリー可視化用）
- **状態管理:** React Context API（小規模なため）

## 2.1. Core Components

### Gemini API Integration
-   **Location**: `backend/app/clients/gemini_client.py`
-   **Purpose**: This client is responsible for all interactions with the Google Gemini API. It handles tasks such as text generation, summarization, and potentially other generative AI functionalities required by the application.
-   **Configuration**:
    -   Requires the `GEMINI_API_KEY` environment variable to be set with a valid API key for authentication.
    -   The necessary library `google-generativeai` has been added to `backend/requirements.txt`.
-   **Error Handling**: The client includes error handling for API communication issues and other unexpected problems, typically returning empty results or raising exceptions as appropriate.

## 3. ディレクトリ構造

```
TransparentResearchExplorer/
├── backend/
│   ├── app/
│   │   └── main.py         # FastAPI アプリケーションのエントリポイント
│   ├── api/                # API ルーター定義
│   ├── core/               # 設定、共通関数など
│   ├── models/             # SQLAlchemy モデル定義
│   ├── schemas/            # Pydantic スキーマ定義
│   └── requirements.txt    # Python 依存ライブラリ
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/     # React コンポーネント
│   │   ├── pages/          # ページコンポーネント
│   │   ├── services/       # API 通信サービス
│   │   ├── contexts/       # React Context
│   │   └── App.js
│   ├── package.json
│   └── ...
├── requirement_definition.md
├── task_breakdown.md
└── README.md
```

## 4. セットアップ方法

### バックエンド (FastAPI)

1.  **リポジトリをクローンします。**
2.  **バックエンドディレクトリに移動します:**
    ```bash
    cd backend
    ```
3.  **Python 仮想環境を作成し、アクティベートします (推奨):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate   # Windows
    ```
4.  **必要なライブラリをインストールします:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **FastAPI 開発サーバーを起動します:**
    ```bash
    uvicorn app.main:app --reload
    ```
    デフォルトでは `http://127.0.0.1:8000` で起動します。

### フロントエンド (React)

1.  **フロントエンドディレクトリに移動します:**
    ```bash
    cd frontend
    ```
2.  **必要なライブラリをインストールします:**
    ```bash
    npm install
    # または yarn install
    ```
3.  **開発サーバーを起動します:**
    ```bash
    npm start
    # または yarn start
    ```
    デフォルトでは `http://localhost:3000` で起動します。

## 5. API 仕様 (主要エンドポイント例)

### バックエンド API

-   **`POST /api/queries/generate`**: 初期キーワードから関連クエリリストを生成します。
    -   リクエストボディ: `{ "keywords": "初期キーワード" }`
    -   レスポンス: `{ "queries": ["関連クエリ1", "関連クエリ2", ...] }`
-   **`POST /api/papers/search`**: クエリリストから論文を検索し、基本情報を返します。
    -   リクエストボディ: `{ "queries": ["クエリ1", "クエリ2"] }`
    -   レスポンス: 論文情報のリスト
-   **`POST /api/papers/score`**: 論文情報とクエリから関連性スコアと理由を生成します。
    -   リクエストボディ: `{ "paper_info": {...}, "query": "..." }`
    -   レスポンス: `{ "score": 0.85, "reason": "..." }`
-   **`POST /api/papers/summary`**: 選択された論文群から集合的な要約を生成します。
    -   リクエストボディ: `{ "paper_ids": ["id1", "id2"] }`
    -   レスポンス: `{ "summary": "生成された要約文" }`

詳細なAPI仕様は、開発の進行とともに更新・追記されます。

## 6. コーディング規約

-   **バックエンド:**
    -   PEP 8 に準拠します。
    -   型ヒントを積極的に使用します。
    -   docstring は Google スタイルを推奨します。
-   **フロントエンド:**
    -   Prettier, ESLint を導入し、整形と静的解析を徹底します。
    -   コンポーネント名はパスカルケース (`MyComponent`)、ファイル名はケバブケース (`my-component.js`) を基本とします。
-   **共通:**
    -   コミットメッセージは Conventional Commits 形式を推奨します。

## 7. ブランチ戦略

-   `main` (または `master`) ブランチ: 保護され、直接コミットは行いません。リリース可能な安定バージョンを保持します。
-   `develop` ブランチ: 開発のベースとなるブランチ。`main` から作成し、フィーチャーブランチのマージ先となります。
-   フィーチャーブランチ (`feature/xxx`): 各機能開発は `develop` からこのブランチを作成して行います。
    -   例: `feature/arxiv-api-integration`, `feature/query-visualization`
-   プルリクエスト (PR): フィーチャーブランチから `develop` へのマージは、必ずPRを作成し、コードレビューを経て行います。

## 8. その他開発上のポイント

-   **コードレビュー:** すべてのPRは、少なくとも1名の他のメンバーによってレビューされることを必須とします。
-   **テスト:** 単体テストや結合テストを可能な範囲で記述し、コードの品質を担保します。
-   **定期的な統合:** 細かい単位でPRをマージし、大きなコンフリクトを未然に防ぎます。
-   **ドキュメント:** この `README.md` を含め、プロジェクトに関するドキュメントは常に最新の状態を保つよう努めます。

---

この `README.md` はプロジェクトの進行に合わせて適宜更新してください。
