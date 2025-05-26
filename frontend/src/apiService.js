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
  }
};

export default apiService;
