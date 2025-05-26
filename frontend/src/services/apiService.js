const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiService = {
  fetchData: async (endpoint) => {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },

  generateQuery: async (initialKeywords) => {
    const response = await fetch(`${BASE_URL}/api/queries/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ initial_keywords: initialKeywords }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate query');
    }

    return response.json();
  },

  fetchQueryTreeData: async () => {
    const response = await fetch(`${BASE_URL}/api/queries/tree`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch query tree data');
    }

    return response.json();
  },

  searchPapers: async (query) => {
    const response = await fetch(`${BASE_URL}/api/papers/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Failed to search papers');
    }

    return response.json();
  },

  getPaperScore: async (paper, query) => {
    const response = await fetch(`${BASE_URL}/api/papers/score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ paper, query }),
    });

    if (!response.ok) {
      throw new Error('Failed to get paper score');
    }

    return response.json();
  },

  searchResearchTree: async (naturalLanguageQuery, maxResultsPerQuery = 5, maxQueries = 5) => {
    try {
      console.log('Sending request to research-tree endpoint:', {
        naturalLanguageQuery,
        maxResultsPerQuery,
        maxQueries
      });

      const response = await fetch(`${BASE_URL}/api/research-tree`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          natural_language_query: naturalLanguageQuery,
          max_results_per_query: maxResultsPerQuery,
          max_queries: maxQueries
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          `検索に失敗しました。ステータス: ${response.status}${
            errorData ? ` - ${errorData.detail || JSON.stringify(errorData)}` : ''
          }`
        );
      }

      const data = await response.json();
      console.log('Received response from research-tree endpoint:', data);
      return data;
    } catch (error) {
      console.error('Error in searchResearchTree:', error);
      throw error;
    }
  },

  /**
   * ストリーミングAPIで逐次データを受信する
   * @param {string} naturalLanguageQuery
   * @param {function} onMessage - 各データ受信時に呼ばれるコールバック
   * @param {number} maxResultsPerQuery
   * @param {number} maxQueries
   * @returns {Promise<void>} 完了時にresolve
   */
  searchResearchTreeStream: async (
    naturalLanguageQuery,
    onMessage,
    maxResultsPerQuery = 5,
    maxQueries = 5
  ) => {
    const response = await fetch(`${BASE_URL}/api/research-tree/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        natural_language_query: naturalLanguageQuery,
        max_results_per_query: maxResultsPerQuery,
        max_queries: maxQueries
      }),
    });
    if (!response.ok || !response.body) {
      throw new Error('ストリーミングAPIの接続に失敗しました');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let lines = buffer.split('\n\n');
      buffer = lines.pop(); // 最後は未完了の可能性
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6);
            const data = JSON.parse(jsonStr);
            onMessage(data);
          } catch (e) {
            console.error('ストリーミングデータのパースエラー', e, line);
          }
        }
      }
    }
  }
};

export default apiService;
