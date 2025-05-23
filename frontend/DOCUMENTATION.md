# フロントエンドドキュメント

このドキュメントは、Transparent Research Explorer アプリケーションのフロントエンドアーキテクチャ、コンポーネント、状態管理、API連携、およびデータフローの概要を日本語で提供します。

## 全体アーキテクチャ

フロントエンドは、React を使用して構築されたシングルページアプリケーション（SPA）です。

-   **`index.js`**: React アプリケーションの標準的なエントリーポイントであり、メインの `<App />` コンポーネントを `public/index.html` 内の 'root' DOM 要素に描画します。
-   **`App.js`**: アプリケーションのルートコンポーネントを定義します。主要なレイアウト構造（`Header`、`MainContent`、`Footer` コンポーネント）を設定し、`AppContext` から `AppProvider` を使用してアプリケーション全体をラップし、グローバルコンテキストを提供します。

## 主要コンポーネントとその役割

-   **`pages/HomePage.js`**:
    -   アプリケーションの主要なUIとロジックのオーケストレーターとして機能します。
    -   検索キーワード、クエリツリーデータ、選択されたクエリ、論文検索結果、フィルター設定など、アプリケーションの多くの状態を管理します。
    -   キーワードの送信、ツリーからのクエリ選択、フィルターの適用、論文検索のトリガーなど、ユーザーインタラクションを処理します。

-   **`components/QueryInputForm.js`**:
    -   ユーザーが初期キーワード（研究テーマなど）を入力するためのテキスト入力フィールドと送信ボタンを提供します。
    -   親コンポーネント（`HomePage`）から `props` を介して送信ハンドラー関数を受け取り、フォーム送信時にその関数を呼び出します。

-   **`components/PaperCard.js`**:
    -   個々の研究論文の情報をカード形式で表示します。
    -   `props` として、論文の詳細（タイトル、著者、要約、URLなど）と現在のクエリ文字列を受け取ります。
    -   論文の関連性スコアが `props` で提供されていない場合、`apiService.getPaperScore` を呼び出して動的に取得できます。スコア取得中はローディングインジケーターが表示されます。

-   **`components/PaperCardGrid.js`**:
    -   論文オブジェクトのリストと現在のクエリ文字列を `props` として受け取ります。
    -   これらの論文を `PaperCard` コンポーネントのグリッドとして表示します。各 `PaperCard` には、個々の論文データとクエリ文字列が渡されます。

-   **`components/QueryTreeVisualizer.js`**:
    -   D3.js ライブラリを使用して、クエリの階層構造を視覚的に表示します。
    -   ツリーのノードはインタラクティブであり、ユーザーがノードをクリックすると、`props` で渡された `onQuerySelect` コールバック関数が選択されたクエリデータ（通常はクエリ名）を引数として呼び出されます。

-   **`components/FilterPanel.js`**:
    -   表示されている論文結果をユーザーがフィルタリングするためのUI要素（例：日付範囲ピッカー、関連性スコアスライダー、カテゴリ選択チェックボックスなど）を提供します。
    -   ユーザーがフィルター条件を変更すると、`props` で渡されたフィルター適用ハンドラー（通常は `HomePage` の関数）が呼び出されます。

-   **`components/Header.js`**:
    -   アプリケーションのヘッダー部分をレンダリングします。通常、アプリケーションのタイトルや主要なナビゲーションリンクが含まれます。

-   **`components/Footer.js`**:
    -   アプリケーションのフッター部分をレンダリングします。著作権情報や補足的なリンクなどが含まれることがあります。

-   **`components/MainContent.js`**:
    -   ページの主要なコンテンツエリア（このアプリケーションでは主に `HomePage` がレンダリングする内容）をラップするレイアウトコンポーネントです。

## 状態管理

-   **`contexts/AppContext.js`**:
    -   React の Context API を使用して、グローバルな状態管理のための `AppContext` と `AppProvider` を定義します。
    -   `AppProvider` は `data` という状態変数とそれを更新するための `setData` 関数を初期化します。
    -   **現在の利用状況**: `AppProvider` はアプリケーション全体をラップしていますが、提供されるグローバルな `data` コンテキストは、主要な機能においては現時点では活発には使用されていません。ほとんどの複雑な状態は `HomePage` コンポーネント内でローカルに管理されています。

-   **ローカル状態 (Local State)**:
    -   **`pages/HomePage.js`**: `useState` フックを広範囲に使用して、以下のような多くのローカル状態を管理します：
        -   ユーザーが入力した初期キーワード。
        -   バックエンドから生成または取得されたクエリツリーのデータ。
        -   `QueryTreeVisualizer` で現在選択されているクエリ。
        -   APIから取得した論文検索結果のリスト。
        -   `FilterPanel` でユーザーが設定した現在のフィルター値（日付範囲、関連性スコア範囲、選択カテゴリなど）。
    -   他のコンポーネント（例: `QueryInputForm`, `PaperCard`）も、フォーム入力値やローディング状態など、自身のUIや機能を管理するために `useState` を使用します。

## API連携 (`services/apiService.js`)

全てのAPI呼び出しは、`http://localhost:8080` をベースURLとして使用します。

-   **`generateQuery(initialKeywords)`**:
    -   **メソッド**: `POST`
    -   **URL**: `http://localhost:8080/api/queries/generate`
    -   **送信データ**: ユーザーが入力した初期キーワード (`{ initial_keywords: initialKeywords }`)。
    -   **期待されるレスポンス**: バックエンドによって生成されたクエリツリー構造（例: `{ original_query: "string", related_queries: [{ query: "string", description: "string" }, ...] }`）。このデータは `QueryTreeVisualizer` で使用されます。

-   **`searchPapers(query, filters)`**:
    -   **メソッド**: `POST`
    -   **URL**: `http://localhost:8080/api/papers/search`
    -   **送信データ**: ユーザーが選択したクエリ文字列と、`FilterPanel` で設定された現在のフィルター基準 (`{ query: "string", filters: {...} }`)。
    -   **期待されるレスポンス**: 指定されたクエリとフィルター条件に一致する研究論文のリスト。

-   **`getPaperScore(paper, query)`**:
    -   **メソッド**: `POST`
    -   **URL**: `http://localhost:8080/api/papers/score`
    -   **送信データ**: 関連性スコアを評価する対象の論文詳細（タイトル、著者、要約など）と、評価の文脈となるクエリ文字列 (`{ paper: { title: "string", authors: [...], abstract: "string" }, query: "string" }`)。
    -   **期待されるレスポンス**: 論文の関連性スコア（通常0から1の間の浮動小数点数）と、そのスコアの根拠を示す説明文（例: `{ score: float, explanation: "string" }`）。

-   **`fetchQueryTreeData()`**:
    -   **メソッド**: `GET`
    -   **URL**: `http://localhost:8080/api/queries/tree`
    -   **目的**: クエリツリー全体のデータをバックエンドから取得します。ただし、現在の主なデータフローでは `generateQuery` が `HomePage` のクエリツリーデータを供給するため、このAPIの使用頻度は低い可能性があります（例：初期ロード時や特定の更新シナリオなど）。

## データフロー

1.  ユーザーは `HomePage` 上の `QueryInputForm` に初期キーワードを入力し、送信します。
2.  `HomePage` は入力されたキーワードを使用して `apiService.generateQuery` を呼び出します。
3.  APIからのレスポンス（クエリツリーデータ）は `HomePage` の状態変数に保存され、`QueryTreeVisualizer` コンポーネントに `props` として渡されて表示されます。
4.  ユーザーは `QueryTreeVisualizer` に表示されたクエリツリーのノード（特定のクエリを表す）をクリックします。
5.  このクリックアクションにより、`QueryTreeVisualizer` の `onQuerySelect` プロップで指定された `HomePage` のコールバック関数が、選択されたクエリ名を引数として実行されます。
6.  `HomePage` は、受け取ったクエリ名と `FilterPanel` で現在設定されているフィルター条件を使用して `apiService.searchPapers` を呼び出し、関連する論文を検索します。
7.  検索結果の論文リストは `HomePage` の状態変数に保存され、`PaperCardGrid` コンポーネントに `props` として渡されます。
8.  `PaperCardGrid` は、受け取った論文リストを基に複数の `PaperCard` コンポーネントをレンダリングします。各 `PaperCard` は個々の論文情報を表示し、必要に応じて（スコアが未提供の場合）`apiService.getPaperScore` を呼び出して関連性スコアを動的に取得・表示します。
9.  ユーザーは `FilterPanel` を使用して表示されている論文に対するフィルター条件（日付範囲、関連性スコア、カテゴリなど）を変更できます。
10. フィルター条件が変更されると、`HomePage` は自身のフィルタ状態を更新し、新しいフィルター条件と現在選択されているクエリを使用して `apiService.searchPapers` を再度呼び出し、論文リストを更新します。

## ルーティング

このアプリケーションは現在、シングルページアプリケーション（SPA）として構成されています。React Router のような明示的なルーティングライブラリは導入されておらず、全てのコンテンツ表示とナビゲーションは `HomePage` コンポーネント内、またはその子コンポーネントの状態変更と条件付きレンダリングによって管理されています。

---
