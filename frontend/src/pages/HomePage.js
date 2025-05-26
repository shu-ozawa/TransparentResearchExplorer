import React, { useState, useEffect, useCallback, useMemo } from 'react';
import QueryInputForm from '../components/QueryInputForm';
import PaperCardGrid from '../components/PaperCardGrid';
import apiService from '../services/apiService';
import QueryTreeVisualizer from '../components/QueryTreeVisualizer';
import FilterPanel from '../components/FilterPanel';
import PaperDetailSidebar from '../components/PaperDetailSidebar'; // Import the sidebar

const HomePage = () => {
  const [researchData, setResearchData] = useState(null);
  const [selectedPaperForSidebar, setSelectedPaperForSidebar] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [selectedQuery, setSelectedQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePaperNodeClick = (paperData) => {
    setSelectedPaperForSidebar(paperData);
    setIsSidebarOpen(true);
  };

  const handleCloseSidebar = () => {
    setIsSidebarOpen(false);
    // Optionally delay setting paper to null for animation:
    // setTimeout(() => setSelectedPaperForSidebar(null), 300); // Adjust delay to match CSS transition
  };

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.searchResearchTree(query);
      console.log('Research tree search results:', result);

      setResearchData(result);
      
      // 論文データを整形
      const allPapers = result.query_nodes.flatMap(node => 
        node.papers.map(paper => ({
          ...paper,
          queryContext: node.description, // Keep context if needed by PaperCardGrid
          // Ensure all fields required by PaperDetailSidebar are present
          // relevanceScore: paper.relevance_score, // already in paper
          // date: new Date(paper.published_date).toLocaleDateString() // PaperDetailSidebar will format date
        }))
      );

      setSearchResults(allPapers);
      setFilteredResults(allPapers); // Apply initial filters or show all
      setSelectedQuery(result.research_goal || query); // Use research_goal if available
    } catch (error) {
      console.error('検索エラー:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Filtering state
  const [dateRange, setDateRange] = useState([0, 100]);
  const [relevanceRange, setRelevanceRange] = useState([0, 1]);
  const [selectedCategories, setSelectedCategories] = useState([]);

  const applyFilters = useCallback((results) => {
    if (!results) return;
    
    let filtered = results;

    // Filter by date range
    filtered = filtered.filter(paper => {
      const paperDate = new Date(paper.published_date);
      const today = new Date();
      const monthsDiff = (today.getFullYear() - paperDate.getFullYear()) * 12 +
                       (today.getMonth() - paperDate.getMonth());
      return monthsDiff >= dateRange[0] && monthsDiff <= dateRange[1];
    });

    // Filter by relevance score
    filtered = filtered.filter(paper =>
      paper.relevance_score >= relevanceRange[0] &&
      paper.relevance_score <= relevanceRange[1]
    );

    // Filter by selected categories
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(paper =>
        paper.categories.some(category => selectedCategories.includes(category))
      );
    }

    setFilteredResults(filtered);
  }, [dateRange, relevanceRange, selectedCategories]);

  useEffect(() => {
    if (searchResults.length > 0) {
      applyFilters(searchResults);
    }
  }, [searchResults, applyFilters]);

  // 利用可能なカテゴリを動的に取得
  const categories = useMemo(() => {
    if (!searchResults.length) return [];
    return [...new Set(searchResults.flatMap(paper => paper.categories))];
  }, [searchResults]);

  return (
    <div className="home-page">
      <h1>Transparent Research Explorer</h1>

      <QueryInputForm 
        onSubmit={handleSearch}
        initialValue={selectedQuery} // This should be researchData.research_goal ideally
        loading={loading}
      />

      {error && <div className="error-message">{error}</div>}

      {researchData?.research_goal && (
        <div className="research-goal">
          <h2>Research Goal:</h2>
          <p>{researchData.research_goal}</p>
        </div>
      )}

      {researchData && (
        <QueryTreeVisualizer
          researchData={researchData} // Pass the full researchData object
          onPaperNodeClick={handlePaperNodeClick} // Pass the click handler
        />
      )}

      {searchResults.length > 0 && (
        <FilterPanel
          dateRange={dateRange}
          setDateRange={setDateRange}
          relevanceRange={relevanceRange}
          setRelevanceRange={setRelevanceRange}
          categories={categories}
          selectedCategories={selectedCategories}
          setSelectedCategories={setSelectedCategories}
        />
      )}

      {loading ? (
        <div className="loading">Searching...</div>
      ) : (
        <>
          {filteredResults.length > 0 ? (
            <>
              <h2>Search Results: {filteredResults.length} papers</h2>
              <PaperCardGrid papers={filteredResults} />
            </>
          ) : (
            searchResults.length > 0 && <p>No results match the selected filters.</p>
          )}
        </>
      )}

      <PaperDetailSidebar
        paper={selectedPaperForSidebar}
        isOpen={isSidebarOpen}
        onClose={handleCloseSidebar}
      />
    </div>
  );
};

export default HomePage;
