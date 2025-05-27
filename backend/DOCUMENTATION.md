# Transparent Research Explorer バックエンドドキュメント

このドキュメントは、Transparent Research Explorer（以下、TRE）アプリケーションのバックエンドシステムに関する包括的な技術概要を提供します。主な対象読者は、本システムの開発・運用に携わるエンジニアです。アーキテクチャ、APIエンドポイント、データベース設計、外部サービス連携、主要な技術スタックについて詳細に解説します。

## 1. 全体アーキテクチャ

TREバックエンドは、PythonのモダンなWebフレームワークであるFastAPIを基盤として構築されています。システムの保守性と拡張性を高めるため、関心の分離 (Separation of Concerns) を重視したモジュラー設計を採用しています。主要なコードコンポーネントは、以下のディレクトリ構造で体系的に管理されています。

-   **`backend/app/`**: FastAPIアプリケーションのコアロジックを格納します。これには、アプリケーションインスタンスの生成と設定を行う`main.py`や、Google Gemini APIなどの外部サービスとの連携を担うクライアントモジュール（例：`clients/gemini_client.py`）が含まれます。
-   **`backend/api/`**: 外部API（例：arXiv学術論文データベース）との通信処理と、TRE自身が公開するAPIエンドポイントの定義を担当します。`arxiv_client.py`のようなクライアント実装や、`endpoints/`ディレクトリ内に配置される`arxiv.py`（arXiv検索関連）および`research_tree.py`（研究ツリー生成関連）といったエンドポイント定義ファイルが含まれます。
-   **`backend/core/`**: アプリケーション全体の動作に不可欠な基盤機能を提供します。具体的には、データベースの接続設定、セッション管理（`database.py`）、設定値の管理などが該当します。
-   **`backend/models/`**: データベースのテーブル構造を定義するSQLAlchemyのORM（Object-Relational Mapper）モデル（例：`paper.py`）が格納されます。これにより、Pythonオブジェクトを通じて直感的にデータベース操作を行えます。
-   **`backend/schemas/`**: データ検証、シリアル化、APIドキュメントの自動生成に用いられるPydanticモデルを管理します。`arxiv_schema.py`のような汎用的なスキーマや、各エンドポイント固有のリクエスト・レスポンススキーマが定義されます。

### 1.1. `backend/app/main.py` - FastAPIアプリケーションエントリーポイント

`app/main.py`は、TREバックエンドアプリケーションの起動点であり、システム全体の挙動を統括する中心的な役割を果たします。主な責務は以下の通りです。

-   **FastAPIアプリケーションの初期化**: `FastAPI`クラスのインスタンスを生成し、アプリケーション名、バージョン、説明といったグローバル設定を適用します。
-   **データベースのセットアップ**: アプリケーション起動時に`core.database`モジュールの`create_db_and_tables()`関数を呼び出します。これにより、`models/`ディレクトリで定義されたORMモデルに基づき、SQLiteデータベース内に必要なテーブルが自動的に作成されます。（補足：より複雑なアプリケーション構成やアプリケーションファクトリパターンを採用する場合、この初期化処理はモジュールレベルでの直接実行ではなく、`@app.on_event("startup")`デコレータを用いたイベントハンドラ内で実行することが推奨される場合があります。）
-   **APIルーターの登録**: `api.endpoints`モジュール群（現在は`arxiv.py`と`research_tree.py`）から、各機能に対応するAPIルーターを読み込み、アプリケーションに登録します。これにより、エンドポイントが機能毎（例：`/api/arxiv`, `/api/research-tree`）に整理され、管理とバージョン管理が容易になります。
-   **ルートエンドポイントの定義**: アプリケーションのヘルスチェックや、基本的な動作確認を目的とした、ルートパス (`/`) へのGETリクエストに対するシンプルな応答エンドポイントを設けています。

## 2. APIエンドポイント

TREバックエンドは、フロントエンドアプリケーションや外部システムとの連携のため、`backend/api/endpoints/`ディレクトリ以下で定義された複数のRESTful APIエンドポイントを公開しています。これらのエンドポイントを通じて、データの取得、登録、更新、削除といった操作が可能になります。

### 2.1. arXivエンドポイント (`/api/arxiv`)

`backend/api/endpoints/arxiv.py`にて定義・管理されており、主に学術論文データベースであるarXivからの情報取得に関連する機能を提供します。パスプレフィックスは`/api/arxiv`です。

-   **`GET /search`** 及び **`POST /search`**
    -   **目的**: 指定されたキーワードに基づき、arXivデータベース内の論文を検索します。GETリクエストの場合はURLクエリパラメータで、POSTリクエストの場合はJSON形式のリクエストボディで検索条件を受け付けます。
    -   **入力 (GET)**:
        -   `keyword` (str): 検索キーワード。
        -   `max_results` (int, オプション, デフォルト: 10): 取得する論文の最大件数。
    -   **リクエストボディ (POST)**: `ArxivSearchRequest`スキーマ (`backend/schemas/arxiv_schema.py`で定義) に準拠。
        -   `keyword` (str): 検索キーワード。
        -   `max_results` (int, オプション, デフォルト: 10): 取得する論文の最大件数。
    -   **出力**: `ArxivSearchResponse`スキーマ (`backend/schemas/arxiv_schema.py`で定義) に準拠。
        -   `papers`: `ArxivPaper`オブジェクト (`backend/schemas/arxiv_schema.py`で定義) のリスト。各オブジェクトには、論文ID (`entry_id`)、タイトル (`title`)、著者リスト (`authors`)、要約 (`summary`)、出版日 (`published_date`)、最終更新日 (`updated_date`)、PDF URL (`pdf_url`)、主要カテゴリ (`primary_category`)、全カテゴリ (`categories`) といった詳細情報が含まれます。
        -   `total_results`: レスポンスに含まれる論文の件数。

### 2.2. Research Tree エンドポイント (`/api/research-tree`)

`backend/api/endpoints/research_tree.py`で管理されており、自然言語による問い合わせから研究計画（リサーチツリー）を生成し、関連論文を検索・評価する機能を提供します。パスプレフィックスは`/api`です（`main.py`でのルーター登録設定による）。

-   **`POST /research-tree`**
    -   **目的**: ユーザーが入力した自然言語のクエリに基づき、研究の目標と複数のサブクエリから成るリサーチツリーを生成します。各サブクエリでarXiv論文を検索し、見つかった論文を元の自然言語クエリとの関連性でスコアリングします。
    -   **入力**: `ResearchTreeRequest`スキーマ (`backend/api/endpoints/research_tree.py`で定義) に準拠。
        -   `natural_language_query` (str): ユーザーが入力した自然言語による研究テーマや問い。
        -   `max_results_per_query` (int, オプション, デフォルト: 5): 各サブクエリでarXivから取得する論文の最大件数。
        -   `max_queries` (int, オプション, デフォルト: 5): LLMによって生成されるサブクエリの最大数。
    -   **処理フロー**:
        1.  **研究計画生成**: 入力された`natural_language_query`を基に、LLM（GeminiまたはOllama、`get_llm_client`経由で選択）を用いて研究全体の目標（`research_goal`）と、具体的な複数のサブクエリ（`QueryNode`のリスト）を生成します。各サブクエリには、そのクエリの意図を説明する短い記述（`description`）も含まれます。
        2.  **論文検索**: 生成された各サブクエリについて、`ArxivAPIClient`を使用してarXivデータベースを検索し、関連論文を取得します。
        3.  **関連性評価**: 取得された各論文について、元の`natural_language_query`との関連性をLLMを用いて評価します。評価結果として、0から1の範囲のスコア（`relevance_score`）と、そのスコアの根拠を説明するテキスト（`relevance_explanation`）が生成されます。
    -   **出力**: `SearchTreeResponse`スキーマ (`backend/api/endpoints/research_tree.py`で定義) に準拠。
        -   `original_query` (str): ユーザーが最初に入力した自然言語クエリ。
        -   `research_goal` (str): LLMによって生成された研究全体の目標。
        -   `query_nodes` (list[`QueryNode`]): サブクエリとその結果のリスト。
            -   `QueryNode` (`backend/api/endpoints/research_tree.py`で定義):
                -   `query` (str): LLMによって生成されたサブクエリ文字列。
                -   `description` (str): サブクエリの目的や内容の簡単な説明。
                -   `papers` (list[`ScoredPaper`]): そのサブクエリで見つかった、スコアリング済みの論文リスト。
                -   `paper_count` (int): このサブクエリで見つかった論文の数。
        -   `total_papers` (int): 全てのサブクエリで見つかった論文の総数（重複を含む）。
        -   `total_unique_papers` (int): 全てのサブクエリで見つかったユニークな論文の総数。
        -   `ScoredPaper` (`backend/api/endpoints/research_tree.py`で定義):
            -   `title` (str): 論文タイトル。
            -   `authors` (list[str]): 著者名のリスト。
            -   `abstract` (str): 論文の要約。
            -   `published_date` (datetime): 出版日。
            -   `url` (str): 論文PDFへのURL。
            -   `categories` (list[str]): 論文のカテゴリ。
            -   `arxiv_id` (str): arXivにおける論文の一意な識別子。
            -   `relevance_score` (float): 元の自然言語クエリとの関連性スコア (0.0-1.0)。
            -   `relevance_explanation` (str): スコアの根拠の説明。

-   **`POST /research-tree/stream`**
    -   **目的**: `POST /research-tree`と同様の処理を行いますが、結果を一度に返すのではなく、サーバーサイドイベント (SSE) を利用して段階的に情報をストリーミングします。これにより、フロントエンドは処理の進捗をリアルタイムに表示できます。
    -   **入力**: `ResearchTreeRequest`スキーマ (同上)。
    -   **出力**: イベントストリーム。各イベントは処理の各段階（研究計画生成完了、サブクエリ検索開始、論文発見、関連性スコア計算完了など）に対応するデータを含みます。最終的なデータ構造は`SearchTreeResponse`と同様の情報を段階的に提供します。

-   **`GET /api/research-stats`** (原文ママ、`main.py`での登録パスは`/research-stats`)
    -   **目的**: (現状はプレースホルダーや開発中の可能性があります) おそらく、研究ツリー生成処理に関する統計情報（例：平均処理時間、LLMコール数など）を提供するためのエンドポイントです。詳細な機能は実装に依存します。
    -   **入力**: なし (または特定のフィルタ条件)。
    -   **出力**: 統計情報を含むJSONレスポンス。

## 3. データベース (`backend/core/database.py`, `backend/models/paper.py`)

TREバックエンドは、検索結果のキャッシュおよび一部データの永続化のために、ローカルSQLiteデータベースを利用しています。

-   **データベースファイル**: `tre_cache.db` という名称で、`backend/`ディレクトリ直下に配置されます。
-   **SQLAlchemyの利用**: データベース操作には、Pythonで広く使われているORMであるSQLAlchemyを採用しています。
    -   `backend/core/database.py`: データベースエンジン (`create_engine`で生成) とセッション管理 (`SessionLocal`、FastAPIの依存性注入で利用される`get_db`関数) の設定を行います。また、ORMモデルの基底クラスとなる`Base`や、データベーススキーマ（テーブル群）を初期化する`create_db_and_tables()`関数を提供します。
-   **`Paper`モデル (`backend/models/paper.py`)**:
    -   このSQLAlchemyモデルは、`papers_cache`テーブルの構造を定義します。このテーブルは、arXivから取得した論文のメタデータを格納するためのキャッシュとして機能します。
    -   **主なフィールド**:
        -   `id` (Integer, 主キー): レコードの一意な識別子。
        -   `arxiv_id` (String, 一意, インデックス付き): arXivにおける論文の一意な識別子。検索効率向上のためインデックスが付与されています。
        -   `title` (String): 論文タイトル。
        -   `authors` (JSON): 著者名のリストをJSON形式で保存。
        -   `abstract` (Text): 論文の要約。長文を想定しText型を使用。
        -   `published_date` (DateTime): 出版日。
        -   `url` (String): 主に論文PDFへの直接リンク。
        -   `created_at`, `updated_at` (DateTime): レコードの作成日時と最終更新日時。監査やデータ管理に利用。
    -   **`papers_cache`テーブルの役割**: arXivから取得した論文メタデータをローカルに保存することで、同一論文への繰り返しのリクエストに対して外部APIへの問い合わせを不要にします。これにより、(1) アプリケーションの応答速度の向上、(2) arXivサーバーへの負荷軽減、(3) オフライン時（限定的）のデータ参照可能性、といったメリットが生まれます。特に`/api/queries/search`エンドポイントは、このキャッシュ機構を積極的に活用します。

## 4. 外部サービスとの連携

TREバックエンドは、機能実現のために主に以下の2つの外部サービスと連携しています。

### 4.1. arXiv (`backend/api/arxiv_client.py`)

-   **目的**: 世界的な学術論文プレプリントサーバーであるarXiv.orgから、論文のメタデータ（タイトル、著者、要約、出版日、PDFリンクなど）を検索・取得します。TREの論文検索機能の根幹をなすデータソースです。
-   **連携方法**:
    -   `ArxivAPIClient`クラス (`backend/api/arxiv_client.py`内) が、arXivとの通信ロジックをカプセル化しています。
    -   内部的には、公式の`arxiv` Pythonライブラリを利用してarXiv APIとのインタラクションを行います。
    -   主要メソッドである`search_papers`は、検索キーワードと最大取得件数を引数に取り、arXiv APIへリクエストを送信します。取得した結果は、`ArxivPaper` Pydanticスキーマオブジェクトのリストへと変換され、アプリケーション内で統一的に扱える形式になります。
    -   **リトライ機構**: ネットワークの不安定性や一時的なAPIエラーに対応するため、`tenacity`ライブラリを用いたリトライ機構が実装されています。`ArxivHTTPError`や`ArxivUnexpectedEmptyPageError`といった特定の例外が発生した場合、指数バックオフ戦略（リトライ間隔を徐々に長くする）に基づいて、自動的にリクエストを数回再試行します。これにより、外部サービスとの連携における堅牢性を高めています。

### 4.2. LLMサービス (Gemini / Ollama)

-   **目的**: GoogleのGeminiやオープンソースのOllamaのような大規模言語モデル（LLM）を活用し、高度な自然言語処理機能（研究計画の生成、論文の関連性評価など）をアプリケーションに組み込みます。
-   **連携方法**:
    -   システムは、LLMクライアントの抽象化レイヤー (`backend/app/dependencies.py`内の`get_llm_client`関数) を利用します。この関数は、環境変数（例：`LLM_PROVIDER`）や設定に基づき、`GeminiClient` (`backend/app/clients/gemini_client.py`) または `OllamaClient` (`backend/app/clients/ollama_client.py`) のインスタンスを動的に提供します。
    -   **`GeminiClient`**: Google Gemini APIと通信します。環境変数`GEMINI_API_KEY`に有効なAPIキーが必要です。
    -   **`OllamaClient`**: ローカルまたはリモートで実行されているOllamaサービスと通信します。環境変数`OLLAMA_API_URL`（例: `http://localhost:11434`）でOllamaサーバーのURLを指定し、`OLLAMA_MODEL_NAME`で使用するモデル名を指定します（例: `llama3`）。
    -   各クライアントは、プロンプト文字列を受け取り、選択されたLLMモデルに送信してテキスト応答を生成する`generate_text`や、より複雑な構造化された出力を得るための`generate_structured_text`のようなメソッドを提供します。
    -   **TREアプリケーションにおける具体的な利用例 (`/api/research-tree`エンドポイント内)**:
        -   **研究計画生成**: ユーザーが入力した自然言語クエリ (`natural_language_query`) を基に、研究全体の目標 (`research_goal`) と複数の具体的なサブクエリ (`QueryNode`のリスト、各々に`description`を含む) から成る研究計画を生成します。これは、`research_tree.py`内の`_generate_research_plan`関数（概念）に相当する処理でLLMを利用します。
        -   **関連性評価**: arXivから取得された各論文について、元の`natural_language_query`との関連性を0から1のスコアで評価し（`relevance_score`）、その評価の根拠をテキストで説明します（`relevance_explanation`）。これは、`research_tree.py`内の`_calculate_relevance_score`関数（概念）に相当する処理でLLMを利用します。
    -   クライアント実装には、API呼び出し時の基本的なエラーハンドリングや、レスポンス解析のロジックが含まれています。

## 5. データスキーマ (Pydanticモデル)

TREバックエンドでは、データの構造定義、バリデーション、シリアライゼーションにPydanticモデルを広範に活用しています。

-   **定義場所**:
    -   汎用的なスキーマ:
        -   `backend/schemas/arxiv_schema.py`: arXiv APIからのデータ（論文情報など）に関連するスキーマ（`ArxivPaper`、`ArxivSearchRequest`、`ArxivSearchResponse`）を定義します。
    -   エンドポイント固有のスキーマ:
        -   `backend/api/endpoints/arxiv.py`: `ArxivSearchRequest`はこのエンドポイントでも利用され、主に`arxiv_schema.py`のものが参照されます。
        -   `backend/api/endpoints/research_tree.py`: リサーチツリー生成機能に特化したスキーマ群（`ResearchTreeRequest`、`ScoredPaper`、`QueryNode`、`SearchTreeResponse`）をインラインで定義しています。
-   **Pydanticモデルの主な役割とメリット**:
    -   **データ検証**: APIリクエストとして受け取った入力データが、定義されたスキーマ（型、必須フィールド、値の範囲など）に適合するかを自動的に検証します。スキーマ違反があった場合、FastAPIは詳細なエラー情報を含むHTTP 422レスポンスをクライアントに返却します。これにより、不正なデータによる後続処理のエラーを未然に防ぎます。
    -   **データシリアル化**: Pythonオブジェクト（例：ORMモデルのインスタンス）をJSONなどの形式に変換してAPIレスポンスとして出力する際や、逆にJSONデータをPythonオブジェクトに変換する際に、型の整合性を保ちつつ効率的に処理します。
    -   **APIドキュメント自動生成**: FastAPIはPydanticモデルの定義を解析し、Swagger UI (OpenAPI) やReDocといった対話的なAPIドキュメントを自動生成します。これにより、APIの仕様が常に最新のコードと同期され、開発者はAPIの利用方法を容易に理解できます。APIが「自己文書化」されるため、ドキュメント作成・維持の負担が軽減されます。

### 5.1. `arxiv_schema.py` の主要スキーマ

-   **`ArxivPaper`**: arXiv論文の詳細情報を保持します。
    -   `entry_id` (str): arXivの論文ID。
    -   `title` (str): 論文タイトル。
    -   `authors` (list[str]): 著者リスト。
    -   `summary` (str): 論文要約。
    -   `published_date` (datetime): 出版日。
    -   `updated_date` (datetime): 最終更新日。
    -   `pdf_url` (str): PDFへのURL。
    -   `primary_category` (str): 主要カテゴリ。
    -   `categories` (list[str]): 全カテゴリのリスト。
-   **`ArxivSearchRequest`**: arXiv論文検索API (`/api/arxiv/search`) のリクエストボディ（POST時）またはクエリパラメータ（GET時）を定義します。
    -   `keyword` (str): 検索キーワード。
    -   `max_results` (int, optional, default=10): 最大取得件数。
-   **`ArxivSearchResponse`**: arXiv論文検索APIのレスポンスボディを定義します。
    -   `papers` (list[`ArxivPaper`]): 検索結果の論文リスト。
    -   `total_results` (int): 検索結果の総数。

### 5.2. `research_tree.py` の主要スキーマ

-   **`ResearchTreeRequest`**: リサーチツリー生成API (`/api/research-tree`) のリクエストボディを定義します。
    -   `natural_language_query` (str): ユーザーが入力する自然言語の研究クエリ。
    -   `max_results_per_query` (int, optional, default=5): 各サブクエリでarXivから取得する論文の最大件数。
    -   `max_queries` (int, optional, default=5): LLMによって生成されるサブクエリの最大数。
-   **`ScoredPaper`**: スコアリングされた論文情報を保持します。`ArxivPaper`の情報を基に、関連性スコアと説明が付与されます。
    -   `title` (str): 論文タイトル。
    -   `authors` (list[str]): 著者リスト。
    -   `abstract` (str): 論文要約（`summary`から名称変更される可能性あり、実装確認要）。
    -   `published_date` (datetime): 出版日。
    -   `url` (str): PDFへのURL (`pdf_url`から名称変更される可能性あり)。
    -   `categories` (list[str]): 論文カテゴリ。
    -   `arxiv_id` (str): arXivの論文ID (`entry_id`から名称変更される可能性あり)。
    -   `relevance_score` (float): 元の自然言語クエリとの関連性スコア (0.0-1.0)。
    -   `relevance_explanation` (str): スコアの根拠の説明。
-   **`QueryNode`**: リサーチツリー内の各サブクエリとその結果を保持します。
    -   `query` (str): LLMによって生成されたサブクエリ文字列。
    -   `description` (str): サブクエリの目的や内容の簡単な説明。
    -   `papers` (list[`ScoredPaper`]): そのサブクエリで見つかったスコアリング済み論文リスト。
    -   `paper_count` (int): このサブクエリで見つかった論文の数。
-   **`SearchTreeResponse`**: リサーチツリー生成APIのレスポンスボディを定義します。
    -   `original_query` (str): ユーザーが最初に入力した自然言語クエリ。
    -   `research_goal` (str): LLMによって生成された研究全体の目標。
    -   `query_nodes` (list[`QueryNode`]): サブクエリとその結果のリスト。
    -   `total_papers` (int): 全てのサブクエリで見つかった論文の総数（重複を含む場合あり）。
    -   `total_unique_papers` (int): 全てのサブクエリで見つかったユニークな論文の総数。

## 6. 主要な依存関係 (`backend/requirements.txt`)

TREバックエンドは、以下の主要なPythonライブラリに依存して構築されています。これらのライブラリは`backend/requirements.txt`ファイルにリストされており、`pip install -r backend/requirements.txt`コマンドで一括インストール可能です。

-   **`fastapi`**: Python 3.7+の型ヒントを活用した、API開発のためのモダンで高性能なWebフレームワーク。非同期処理に対応し、高いパフォーマンスと開発効率を実現します。
-   **`uvicorn[standard]`**: FastAPIアプリケーションを実行するためのASGI (Asynchronous Server Gateway Interface) サーバー。`[standard]`オプションには、WebSocketやHTTP/2プロトコルのサポートなど、実運用に有用な追加機能が含まれます。
-   **`google-generativeai`**: GoogleのGeminiをはじめとする生成AIモデルのAPIを利用するための公式Pythonクライアントライブラリ。
-   **`sqlalchemy`**: PythonにおけるSQL操作とORMの標準的なライブラリ。データベースとの対話を抽象化し、Pythonicなコードでデータアクセスを可能にします。
-   **`aiosqlite`**: 非同期処理を特徴とするFastAPIアプリケーション内で、SQLAlchemyを通じてSQLiteデータベースを非同期に操作するために必要なドライバー。
-   **`arxiv`**: arXiv APIのPythonラッパー。論文メタデータの検索・取得処理を簡略化します。
-   **`httpx`**: Python 3対応の多機能なHTTPクライアントライブラリ。FastAPIのAPIエンドポイントをテストする際に用いられる`TestClient`の内部依存関係としても利用されます。
-   **`tenacity`**: 汎用のリトライ処理ライブラリ。`ArxivAPIClient`において、arXiv API呼び出し時のネットワークエラーなど、一時的な障害からの回復性を高めるために使用されます。
-   **`pytest`, `pytest-asyncio`, `pytest-mock`**: これらはアプリケーションのテストコード記述・実行を支援するライブラリ群です（直接的なランタイム依存ではありませんが、開発プロセスにおいて極めて重要です）。`pytest`は高機能なテストフレームワーク、`pytest-asyncio`は非同期コードのテストを、`pytest-mock`はオブジェクトのモック化（テストダブルの作成）を容易にします。

このドキュメントが、TREバックエンドシステムの構成要素とその相互作用について、明確な理解の一助となれば幸いです。
---
