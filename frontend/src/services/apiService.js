const apiService = {
  fetchData: async (endpoint) => {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },

  generateQuery: async (initialKeywords) => {
    const response = await fetch('http://localhost:8080/api/queries/generate', {
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
    const response = await fetch('http://localhost:8080/api/queries/tree', {
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
    const response = await fetch('http://localhost:8080/api/papers/search', {
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
    const response = await fetch('http://localhost:8080/api/papers/score', {
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
};

export default apiService;
