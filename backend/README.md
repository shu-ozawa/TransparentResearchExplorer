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
uvicorn app.main:app --reload
```

バックエンドサーバーは`http://127.0.0.1:8000`で利用可能になります。

## APIエンドポイント

### クエリ生成
- **POST /api/queries/generate**: Gemini APIを使用して初期キーワードから関連クエリを生成します。

リクエストボディの例：
```json
{
  "initial_keywords": "machine learning in healthcare"
}
```

レスポンスの例：
```json
{
  "original_query": "machine learning in healthcare",
  "related_queries": [
    {
      "query": "deep learning for medical image analysis",
      "description": "MRIやCTスキャンなどの医用画像を分析するための深層学習技術に焦点を当てています。"
    },
    {
      "query": "reinforcement learning in personalized medicine",
      "description": "個別化された治療計画を作成するための強化学習の応用を探求します。"
    }
  ]
}
```

### arXiv検索
- **POST /api/arxiv/search**: キーワードを使用してarXivの論文を検索します。
- **GET /api/arxiv/search**: クエリパラメータを使用して論文を検索します。

## 開発メモ

このプロジェクトはWebフレームワークとしてFastAPI、データベース操作にはSQLAlchemyを使用しています。関連検索クエリの生成にはGemini APIクライアント、学術論文の検索にはarXiv APIクライアントを使用しています。
