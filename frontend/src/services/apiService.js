const apiService = {
  fetchData: async (endpoint) => {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },

  generateQuery: async (initialKeywords) => {
    const response = await fetch('/api/generate', {
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
};

export default apiService;
