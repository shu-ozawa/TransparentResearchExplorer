import React, { useState } from 'react'; // Removed useEffect, useCallback, useMemo
import QueryInputForm from '../components/QueryInputForm';
// import PaperCardGrid from '../components/PaperCardGrid'; // Removed
import apiService from '../services/apiService';
import QueryTreeVisualizer from '../components/QueryTreeVisualizer';
// import FilterPanel from '../components/FilterPanel'; // Removed
import PaperDetailSidebar from '../components/PaperDetailSidebar';

const HomePage = () => {
  const [researchData, setResearchData] = useState(null);
  const [selectedPaperForSidebar, setSelectedPaperForSidebar] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  // Removed searchResults, filteredResults state
  const [selectedQuery, setSelectedQuery] = useState(''); // Retained for QueryInputForm initial value
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePaperNodeClick = (paperData) => {
    setSelectedPaperForSidebar(paperData);
    setIsSidebarOpen(true);
  };

  const handleCloseSidebar = () => {
    setIsSidebarOpen(false);
    // Optionally delay setting paper to null for animation:
    // setTimeout(() => setSelectedPaperForSidebar(null), 300);
  };

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.searchResearchTree(query);
      console.log('Research tree search results:', result);

      setResearchData(result);
      // Removed logic for allPapers, setSearchResults, setFilteredResults
      setSelectedQuery(result.research_goal || query); // Use research_goal if available
    } catch (error) {
      console.error('Search error:', error); // "検索エラー" changed to "Search error"
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Removed Filtering state (dateRange, relevanceRange, selectedCategories)
  // Removed applyFilters function
  // Removed useEffect for applyFilters
  // Removed useMemo for categories

  return (
    <div className="home-page">
      <h1>Transparent Research Explorer</h1>

      <QueryInputForm 
        onSubmit={handleSearch}
        initialValue={selectedQuery} 
        loading={loading}
      />

      {error && <div className="error-message">{error}</div>}

      {!loading && !error && !researchData && (
        <p className="initial-state-message">
          Enter a research topic above to generate and visualize a research network.
        </p>
      )}

      {researchData?.research_goal && (
        <div className="research-goal">
          <h2>Research Goal:</h2>
          <p>{researchData.research_goal}</p>
        </div>
      )}

      {researchData && (
        <QueryTreeVisualizer
          researchData={researchData} 
          onPaperNodeClick={handlePaperNodeClick}
        />
      )}

      {/* The main loading indicator for search operation */}
      {loading && <div className="loading">Searching...</div>}
      
      {/* QueryTreeVisualizer renders null if !researchData, so no specific message needed here if it's just empty.
          The initial-state-message above covers the "before first search" scenario.
          If a search returns an empty result (e.g. result.query_nodes is empty but researchData object exists), 
          QueryTreeVisualizer would still render its stats (possibly all zeros) and legend,
          but the graph area would be empty. This is an acceptable state.
      */}

      <PaperDetailSidebar
        paper={selectedPaperForSidebar}
        isOpen={isSidebarOpen}
        onClose={handleCloseSidebar}
      />
    </div>
  );
};

export default HomePage;
