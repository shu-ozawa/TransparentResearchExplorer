# Transparent Research Explorer バックエンド

これはTransparent Research Explorerアプリケーションのバックエンドサービスです。arXiv論文の検索とGemini AIを使用した関連検索クエリの生成のためのAPIエンドポイントを提供します。

## セットアップ手順

### 1. 新しいCondaの環境を作成
```bash
conda create -n tre-api python=3.12 -y
conda activate tre-api
```

### 2. 依存関係のインストール
```bash
cd backend
pip install -r requirements.txt
```

### 3. 環境変数の設定
`backend`ディレクトリに`.env`ファイルを作成し、GeminiのAPIキーを設定します：
```
GEMINI_API_KEY=your_api_key_here
```

### 4. サーバーの起動
```bash
cd root
uvicorn backend.app.main:app --reload
```

バックエンドサーバーは`http://127.0.0.1:8000`で利用可能になります。

## APIエンドポイント

### リサーチツリー生成
- **POST /api/research-tree**: 自然言語の問い合わせに基づき、研究計画（リサーチツリー）を生成し、関連論文を検索・評価します。LLM（GeminiまたはOllama）を利用して、研究目標と複数のサブクエリを生成し、各サブクエリでarXivから論文を検索後、元の問い合わせとの関連性をスコアリングします。
  - ストリーミング対応版として `POST /api/research-tree/stream` も利用可能です。

リクエストボディの例 (`/api/research-tree`):
```json
{
  "natural_language_query": "machine learning in healthcare",
  "max_results_per_query": 5,
  "max_queries": 3
}
```

レスポンスの概要:
レスポンスはJSON形式で、主に以下の情報を含みます。
- `original_query`: ユーザーが入力した元の自然言語クエリ。
- `research_goal`: LLMによって生成された研究全体の目標。
- `query_nodes`: 複数のサブクエリノードのリスト。各ノードには以下の情報が含まれます。
    - `query`: LLMによって生成された具体的な検索クエリ文字列。
    - `description`: そのサブクエリの意図や内容の簡単な説明。
    - `papers`: 関連するarXiv論文のリスト。各論文にはタイトル、著者、要約、出版日、URL、カテゴリ、そして元の自然言語クエリとの関連性スコアと評価理由が付与されます。
    - `paper_count`: そのサブクエリで見つかった論文の数。
- `total_papers`, `total_unique_papers`: 検索された総論文数とユニークな論文数。

詳細なレスポンススキーマはOpenAPIドキュメント (`/docs`) を参照してください。

### arXiv直接検索
- **POST /api/arxiv/search**: 指定されたキーワードでarXivデータベースから直接論文を検索します。
- **GET /api/arxiv/search**: クエリパラメータを使用して論文を検索します。

リクエストボディの例 (`POST /api/arxiv/search`):
```json
{
  "keyword": "quantum computing",
  "max_results": 10
}
```
レスポンス:
arXivから取得した論文情報のリスト（タイトル、著者、要約、出版日、PDF URLなど）。

## 開発メモ

このプロジェクトはWebフレームワークとしてFastAPI、データベース操作にはSQLAlchemyを使用しています。
主要な機能として、`backend/api/endpoints/research_tree.py`モジュールが自然言語による問い合わせを基にした研究計画の生成、関連論文の検索、およびスコアリング処理を統括しています。
また、大規模言語モデル（LLM）の利用は抽象化されており (`backend/app/dependencies.py`内の`get_llm_client`経由)、Google GeminiやOllamaといった異なるLLMプロバイダーを研究計画生成や論文の関連性評価などのタスクに活用できます。
学術論文の直接検索には`backend/api/arxiv_client.py`経由でarXiv APIクライアントを使用しています。
詳細なアーキテクチャや各コンポーネントの役割については、ルートディレクトリの `README.md` および `backend/DOCUMENTATION.md` を参照してください。
