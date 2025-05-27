# Transparent Research Explorer (TRE) プロトタイプ

## 1. プロジェクト概要

Transparent Research Explorer (TRE) は、arXiv から論文を検索し、検索プロセスとその結果を可視化することで、研究者の先行研究調査を支援するシステムのプロトタイプです。検索クエリの枝分かれ・進化の透明化と、論文選択プロセスの可視化を中心に据え、「AIが何をどのように検索したか」を明示することを目的としています。バックエンドの主要機能の一つとして、自然言語による問い合わせを構造化された研究計画（リサーチツリー）に分解し、関連性の高い論文を検索・スコアリングする `research_tree` モジュールを有しています。

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

### LLM Integration (Gemini, Ollama, etc.)
-   **LLM Client Abstraction**: The system utilizes an abstraction layer (`backend/app/dependencies.py` via `get_llm_client`) to interact with Large Language Models. This allows for flexibility in choosing LLM providers.
-   **Gemini API Client**:
    -   **Location**: `backend/app/clients/gemini_client.py`
    -   **Purpose**: This client handles interactions with the Google Gemini API. It is primarily used within the `research_tree` module for tasks such as:
        -   Generating a structured research plan (research goal and sub-queries) from a user's natural language query.
        -   Evaluating and scoring the relevance of arXiv papers against the user's initial query.
    -   **Configuration**: Requires the `GEMINI_API_KEY` environment variable. The `google-generativeai` library is listed in `backend/requirements.txt`.
-   **Ollama Client**:
    -   **Location**: `backend/app/clients/ollama_client.py`
    -   **Purpose**: Provides an interface to use local or self-hosted LLMs through Ollama. It serves the same purposes as the Gemini client (research plan generation, paper scoring) if selected as the LLM provider.
    -   **Configuration**: Requires `OLLAMA_API_URL` and `OLLAMA_MODEL_NAME` environment variables. The `httpx` library (already a dependency) is used for communication.
-   **Error Handling**: Both clients include error handling for API communication issues.

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

-   **`POST /api/research-tree`**: 自然言語の問い合わせから研究計画（リサーチツリー）を生成し、関連論文を検索・評価します。
    -   リクエストボディ例: `{ "natural_language_query": "大規模言語モデルがソフトウェア開発に与える影響", "max_results_per_query": 3, "max_queries": 3 }`
    -   レスポンス: 研究目標、サブクエリ群、および各サブクエリで見つかったスコアリング済み論文リストを含む構造化された応答 (`SearchTreeResponse`)。論文のスコアリングは元の自然言語クエリとの関連性に基づきます。
-   **`POST /api/research-tree/stream`**: 上記 `/api/research-tree` と同様の処理をストリーミング形式で行い、結果を段階的に返します。
    -   リクエストボディ例: (上記と同様)
    -   レスポンス: サーバーサイドイベント (SSE) ストリーム。
-   **`POST /api/arxiv/search`**: 指定されたキーワードでarXivデータベースを直接検索します。
    -   リクエストボディ例: `{ "keyword": "quantum computing", "max_results": 10 }`
    -   レスポンス: arXiv論文情報のリスト (`ArxivSearchResponse`)。GETリクエスト (`GET /api/arxiv/search?keyword=...&max_results=...`) も利用可能です。

詳細なAPI仕様は、バックエンドのOpenAPIドキュメント (`/docs` または `/redoc`) 及び `backend/DOCUMENTATION.md` を参照してください。

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
