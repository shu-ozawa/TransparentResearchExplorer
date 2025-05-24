# バックエンドドキュメント

このドキュメントは、Transparent Research Explorerアプリケーションのバックエンドアーキテクチャ、APIエンドポイント、データベースセットアップ、外部サービス連携、および主要な依存関係について包括的な概要を提供します。

## 全体のアーキテクチャ

バックエンドはFastAPIフレームワークを使用したPythonアプリケーションです。保守性を高めるために、関心事の分離に基づくモジュラー設計を採用しています。コードは主に以下のディレクトリに整理されています：

-   **`backend/app/`**: メインのFastAPIアプリケーションのセットアップ（`main.py`）と、Google Gemini APIなどの外部サービスとの対話を行うクライアント（`clients/gemini_client.py`）が含まれています。
-   **`backend/api/`**: 外部API（arXiv学術論文サービスなど、`arxiv_client.py`経由）との対話を処理し、アプリケーション自身のAPIエンドポイント（`endpoints/`）の構造を定義します。
-   **`backend/core/`**: アプリケーションの動作に不可欠なコア機能、特にデータベースのセットアップ、設定、セッション管理（`database.py`）を格納します。
-   **`backend/models/`**: データベーステーブルの構造を表すSQLAlchemy Object-Relational Mapper（ORM）モデル（`paper.py`）を定義します。
-   **`backend/schemas/`**: データの検証、シリアル化、およびリクエスト/レスポンスボディの自動API文書化に使用されるPydanticモデル（`arxiv_schema.py`およびエンドポイントファイル内で定義されるその他のモデル）を含みます。

### `backend/app/main.py` - FastAPIアプリケーション

`app/main.py`スクリプトはバックエンドアプリケーションのエントリーポイントであり、中核となります。その責務には以下が含まれます：

-   **FastAPIアプリの初期化**: アプリケーションのタイトルや説明などのグローバル設定を行い、`FastAPI`アプリケーションのインスタンスを作成します。
-   **データベースのセットアップ**: 起動時に`create_db_and_tables()`（`backend.core.database`から）を呼び出し、SQLiteデータベースに必要なすべてのテーブル（`backend/models/`で定義）が作成されていることを確認します。
-   **ルーターの組み込み**: `backend.api.endpoints`モジュールからAPIルーターを組み込みます。各ルーターは関連するエンドポイントを共通のプレフィックス（例：`/api/arxiv`、`/api/queries`、`/api/papers`）の下にグループ化し、API構造を整理しバージョン管理可能にします。
-   **ルートエンドポイント**: ヘルスチェックやシンプルなウェルカムメッセージ用の基本的なGETエンドポイントを`/`に定義します。

## APIエンドポイント

バックエンドは`backend/api/endpoints/`ディレクトリ内で定義された複数のRESTful APIエンドポイントを公開しています。これらのエンドポイントはフロントエンドとの対話とデータ操作を容易にします。

### 1. arXivエンドポイント（`/api/arxiv`）

`backend/api/endpoints/arxiv.py`で管理されています。これらのエンドポイントはarXivリポジトリの検索を可能にします。

-   **`GET /search`**および**`POST /search`**
    -   **目的**: 指定されたキーワードに基づいてarXivの論文を検索します。GETバージョンはパラメータをURLクエリ文字列として受け取り、POSTバージョンはJSONリクエストボディを期待します。
    -   **入力**:
        -   `keyword`（str）: 検索語またはキーワード。
        -   `max_results`（int、オプション、デフォルト：10）: 返す論文の最大数。
    -   **リクエストボディ（POSTの場合）**: `ArxivSearchRequest`スキーマ（`{ "keyword": "...", "max_results": ... }`）
    -   **出力**: `ArxivSearchResponse`スキーマ（`{ "papers": [...], "total_results": ... }`）
        -   `papers`: `ArxivPaper`オブジェクトのリスト。各オブジェクトには`entry_id`、`title`、`authors`、`summary`、`published`日付、`updated`日付、`pdf_url`、`categories`などの詳細が含まれます。
        -   `total_results`: 現在のレスポンスで返された論文の数。

### 2. 論文エンドポイント（`/api/papers`）

`backend/api/endpoints/papers.py`で管理されています。このグループは現在、論文の処理とスコアリングに焦点を当てています。

-   **`POST /score`**
    -   **目的**: 特定のクエリに対する研究論文の関連性スコア（0-1）とテキストによる説明を生成します。これはGemini言語モデルを活用して実現されます。
    -   **入力**: `ScoreRequest`スキーマ
        -   `paper`（オブジェクト）: 論文情報を含みます：
            -   `title`（str）
            -   `authors`（strのリスト）
            -   `abstract`（str）
        -   `query`（str）: 論文と比較するユーザーのクエリ。
    -   **出力**: `RelevanceScoreResponse`スキーマ
        -   `score`（float）: 0.0（関連性なし）から1.0（高い関連性）までの数値スコア。
        -   `explanation`（str）: 割り当てられたスコアの理由を説明するGeminiが生成した簡潔なテキスト。
    -   **Geminiとの対話**: エンドポイントは論文の要約、タイトル、著者とユーザーのクエリを組み合わせた詳細なプロンプトを構築します。このプロンプトはGemini APIに送信され、レスポンスからスコアと説明が抽出されます。

### 3. クエリエンドポイント（`/api/queries`）

`backend/api/endpoints/queries.py`で管理されています。これらのエンドポイントはクエリの生成と論文の検索/キャッシュを処理します。

-   **`POST /generate`**
    -   **目的**: ユーザーが提供した初期キーワードまたは研究テーマに基づいて、関連する検索クエリのリストを生成します。これはGemini言語モデルを使用して、代替的なまたはより具体的なクエリを提案します。
    -   **入力**: `QueryGenerationRequest`スキーマ
        -   `initial_keywords`（str）: ユーザーの開始キーワードまたは研究トピック。
    -   **出力**: `QueryGenerationResponse`スキーマ
        -   `original_query`（str）: ユーザーが提供した初期キーワード。
        -   `related_queries`（オブジェクトのリスト）: 各オブジェクトには以下が含まれます：
            -   `query`（str）: 提案された関連クエリ。
            -   `description`（str）: 関連クエリが焦点を当てる内容の簡単な説明。
    -   **Geminiとの対話**: `initial_keywords`を使用してプロンプトを作成し、Geminiに5-7個の関連クエリとその説明の生成を依頼します。Geminiからのテキストレスポンスは出力形式に構造化されます。

-   **`POST /search`**
    -   **目的**: 提供されたクエリリストを使用してarXivで論文を検索し、結果を統合し、冗長な外部APIコールを最小限に抑えるためにローカルデータベースにキャッシュし、見つかった論文の重要な情報を返します。
    -   **入力**: `SearchQuery`オブジェクトのリスト。各`SearchQuery`オブジェクトには以下が含まれます：
        -   `query`（str）: 特定の検索クエリ文字列。
        -   `max_results`（int、オプション、デフォルト：10）: この特定のクエリの最大結果数。
    -   **出力**: `PaperSearchResponse`オブジェクトのリスト。各オブジェクトには以下が含まれます：
        -   `title`（str）
        -   `authors`（strのリスト）
        -   `summary`（str）
        -   `published_date`（datetime）
        -   `url`（str、通常はPDF URL）
    -   **キャッシュの対話**:
        1.  入力リストの各クエリに対して、システムはまず`ArxivAPIClient`を使用してarXivから論文の`entry_id`リストを取得します。
        2.  次に、これらの`entry_id`を持つ論文がローカルの`papers_cache`データベーステーブル（`Paper`モデル経由）に既に存在するかチェックします。
        3.  論文がキャッシュに見つかった場合、そのデータが直接使用されます。
        4.  論文がキャッシュに見つからない場合、arXivから取得したデータ（`ArxivAPIClient`経由）が将来のリクエストのために`papers_cache`テーブルに保存されます。
        5.  結合された結果（キャッシュされたものと新しく取得したもの）がフォーマットされて返されます。

## データベース（`backend/core/database.py`、`backend/models/paper.py`）

バックエンドはキャッシュとデータ永続化のためにローカルのSQLiteデータベースを使用します。

-   **データベースファイル**: `tre_cache.db`（`backend/`ディレクトリに配置）。
-   **SQLAlchemy**: アプリケーションはObject-Relational Mapper（ORM）としてSQLAlchemyを使用します。
    -   `backend/core/database.py`はデータベースエンジン（`create_engine`）とセッション管理（`SessionLocal`、FastAPI用の`get_db`依存関係）を設定します。また、宣言的モデル定義用の`Base`とデータベーススキーマを初期化する`create_db_and_tables()`関数も提供します。
-   **`Paper`モデル（`backend/models/paper.py`）**:
    -   このSQLAlchemyモデルは`papers_cache`テーブルの構造を定義します。
    -   **フィールドには以下が含まれます**:
        -   `id`（Integer、主キー）
        -   `arxiv_id`（String、一意、インデックス付き）: arXivからの一意の識別子。
        -   `title`（String）
        -   `authors`（JSON）: 著者名のJSON配列として保存。
        -   `abstract`（Text）
        -   `published_date`（DateTime）
        -   `url`（String）: 通常はPDFリンク。
        -   `created_at`、`updated_at`（DateTime）: レコード管理用のタイムスタンプ。
    -   **`papers_cache`テーブルの役割**: このテーブルはarXivから取得した論文メタデータのキャッシュとして機能します。結果をローカルに保存することで、アプリケーションは外部arXiv APIへのコール数を大幅に削減でき、繰り返しのクエリに対する応答時間が速くなり、arXivサーバーへの負荷も軽減されます。`/api/queries/search`エンドポイントはこのキャッシュメカニズムの主要なインターフェースです。

## 外部サービスとの対話

バックエンドは主に2つの外部サービス（arXivとGoogle Gemini）と連携します。

### 1. arXiv（`backend/api/arxiv_client.py`）

-   **目的**: arXiv.org e-printアーカイブから学術論文のメタデータを検索および取得します。
-   **対話**:
    -   `ArxivAPIClient`クラスはarXivとの対話ロジックをカプセル化します。
    -   公式の`arxiv` Pythonライブラリを使用します。
    -   `search_papers`メソッドはキーワードと最大結果数を受け取り、arXiv APIにクエリを送信し、結果を`ArxivPaper` Pydanticスキーマオブジェクトのリストに変換します。
    -   **リトライロジック**: クライアントは`tenacity`ライブラリを使用してリトライ機能を組み込んでいます。arXiv APIへのコールが失敗した場合（例：`ArxivHTTPError`や`ArxivUnexpectedEmptyPageError`など）、指数バックオフを使用して自動的にリクエストを数回再試行し、連携の堅牢性を高めます。

### 2. Gemini（`backend/app/clients/gemini_client.py`）

-   **目的**: 高度なテキスト生成と理解タスクのためにGoogleのGemini大規模言語モデルを活用します。
-   **対話**:
    -   `GeminiClient`クラスはGemini APIとの通信を管理します。
    -   認証のために`GEMINI_API_KEY`を環境変数として設定する必要があります。
    -   主要なメソッド`generate_text(prompt: str)`は、与えられたプロンプトを`gemini-pro`モデルに送信し、生成されたテキストレスポンスを返します。
    -   **アプリケーションでの使用**:
        -   **関連性スコアリング（`/api/papers/score`）**: Geminiを使用して、研究論文がユーザーのクエリにどの程度関連しているかを評価し、数値スコアとテキストによる正当化を生成します。
        -   **関連クエリ生成（`/api/queries/generate`）**: Geminiを使用して、ユーザーの初期キーワードまたは研究テーマに基づいて、関連する、または代替的な検索クエリを提案します。
    -   クライアントにはAPIコールとレスポンス解析の基本的なエラーハンドリングが含まれています。

## データスキーマ（Pydanticモデル）

-   **場所**: `backend/schemas/arxiv_schema.py`（arXiv固有の構造用）および`backend/api/endpoints/`内の各エンドポイントファイル内で他のリクエスト/レスポンスボディ用にインラインで定義されています。
-   **目的**: Pydanticモデルは以下の理由で重要です：
    -   **データ検証**: 入力リクエストデータを自動的に検証します。データが定義されたスキーマに準拠していない場合（例：データ型が間違っている、フィールドが欠落している）、FastAPIは明確なエラーレスポンスを返します。
    -   **データシリアル化**: 出力レスポンスデータの構造化とシリアル化に使用され、一貫性を確保します。
    -   **API文書化**: FastAPIはこれらのPydanticモデルを使用して、期待されるリクエストとレスポンスの形式を示す対話型API文書（例：Swagger UIやReDoc経由）を自動生成します。これによりAPIは自己文書化され、理解と使用が容易になります。

## 主要な依存関係（`backend/requirements.txt`）

バックエンドは以下の主要なPythonライブラリに依存しています：

-   **`fastapi`**: Python 3.7+の標準的な型ヒントに基づいて、APIを構築するための最新の高性能Webフレームワーク。
-   **`uvicorn[standard]`**: FastAPIアプリケーションを実行するためのASGI（Asynchronous Server Gateway Interface）サーバー。`[standard]`オプションにはwebsocketsやhttp/2サポートなどの有用な追加機能が含まれます。
-   **`google-generativeai`**: Geminiを含むGoogleの生成AI APIのための公式Pythonクライアントライブラリ。
-   **`sqlalchemy`**: アプリケーション開発者にSQLの完全な機能と柔軟性を提供するPython SQLツールキットとObject Relational Mapper。データベース対話に使用されます。
-   **`aiosqlite`**: 非同期FastAPIアプリケーションでSQLAlchemyをSQLiteと共に使用するために必要な非同期SQLiteドライバー。
-   **`arxiv`**: arXiv APIのPythonラッパー。論文データの取得に使用されます。
-   **`httpx`**: Python 3用の完全な機能を備えたHTTPクライアント。FastAPIのAPIエンドポイントテスト用の`TestClient`で使用されます。
-   **`tenacity`**: `ArxivAPIClient`でarXiv APIを呼び出す際の一時的なエラーを処理するために使用される汎用リトライライブラリ。
-   **`pytest`、`pytest-asyncio`、`pytest-mock`**: アプリケーションのテストに使用されるライブラリ（ランタイムの直接の一部ではありませんが、開発には重要です）。

このドキュメントはバックエンドシステムのコンポーネントとそれらの相互作用について明確な理解を提供するはずです。
---
