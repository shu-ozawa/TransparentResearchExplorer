const apiService = {
  fetchData: async (endpoint) => {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  },
};

export default apiService;
