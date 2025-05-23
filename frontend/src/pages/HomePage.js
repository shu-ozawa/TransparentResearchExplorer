import React, { useState } from 'react';
import ExampleComponent from '../components/ExampleComponent';
import QueryInputForm from '../components/QueryInputForm';
import PaperCardGrid from '../components/PaperCardGrid';
import apiService from '../services/apiService';
import QueryTreeVisualizer from '../components/QueryTreeVisualizer';
import FilterPanel from '../components/FilterPanel';

const HomePage = () => {
  const [queryTreeData, setQueryTreeData] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [selectedQuery, setSelectedQuery] = useState('');

  const handleKeywordsSubmit = async (keywords) => {
    try {
      const result = await apiService.generateQuery(keywords);
      console.log('Generated queries:', result);

      // Update state with query tree data
      if (result.related_queries && Array.isArray(result.related_queries)) {
        setQueryTreeData({
          name: result.original_query,
          children: result.related_queries.map(q => ({ name: q.query }))
        });
      }
    } catch (error) {
      console.error('Error generating query:', error);
      alert(`Failed to generate query: ${error.message}`);
    }
  };

  // Filtering state
  const [dateRange, setDateRange] = useState([0, 100]);
  const [relevanceRange, setRelevanceRange] = useState([0, 5]);
  const categories = ['cs.AI', 'cs.LG', 'stat.ML', 'physics.hep-th']; // Example categories
  const [selectedCategories, setSelectedCategories] = useState([]);

  const applyFilters = (results) => {
    let filtered = results;

    // Filter by date range (assuming months from now)
    filtered = filtered.filter(paper => {
      const paperDate = new Date(paper.date);
      const today = new Date();
      const monthsDiff = (today.getFullYear() - paperDate.getFullYear()) * 12 +
                         (today.getMonth() - paperDate.getMonth());
      return monthsDiff >= dateRange[0] && monthsDiff <= dateRange[1];
    });

    // Filter by relevance score
    filtered = filtered.filter(paper =>
      paper.relevanceScore >= relevanceRange[0] &&
      paper.relevanceScore <= relevanceRange[1]
    );

    // Filter by selected categories
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(paper =>
        selectedCategories.some(category => paper.categories.includes(category))
      );
    }

    setFilteredResults(filtered);
  };

  const handleQuerySelect = async (query) => {
    setSelectedQuery(query);
    try {
      const results = await apiService.searchPapers(query);
      console.log('Search results:', results);

      // Format the search results for display
      const formattedResults = results.map(paper => ({
        title: paper.title,
        authors: paper.authors,
        date: new Date(paper.published).toLocaleDateString(),
        abstract: paper.abstract,
        relevanceScore: paper.relevance_score,
        categories: paper.categories || [],
      }));

      setSearchResults(formattedResults);
      applyFilters(formattedResults); // Apply filters to the initial results
    } catch (error) {
      console.error('Error searching papers:', error);
      alert(`Failed to search papers: ${error.message}`);
    }
  };

  const loadQueryTreeData = async () => {
    try {
      const data = await apiService.fetchQueryTreeData();
      setQueryTreeData(data);
    } catch (error) {
      console.error('Error fetching query tree data:', error);
    }
  };

  // Apply filters whenever filtering criteria change
  useEffect(() => {
    if (searchResults.length > 0) {
      applyFilters(searchResults);
    }
  }, [dateRange, relevanceRange, selectedCategories]);

  return (
    <div>
      <h1>Transparent Research Explorer</h1>

      {/* Initial keywords input */}
      <QueryInputForm onSubmit={handleKeywordsSubmit} />

      {/* Query Tree Visualizer with clickable queries */}
      {queryTreeData && (
        <>
          <button onClick={loadQueryTreeData}>Reload Query Tree</button>
          <QueryTreeVisualizer
            data={queryTreeData}
            onQuerySelect={handleQuerySelect}
          />
        </>
      )}

      {/* Paper search form (for direct query input) */}
      <div style={{ marginTop: '20px' }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (selectedQuery) {
              handleQuerySelect(selectedQuery);
            }
          }}
        >
          <input
            type="text"
            value={selectedQuery}
            onChange={(e) => setSelectedQuery(e.target.value)}
            placeholder="Enter or select a query to search papers"
            style={{ marginRight: '10px' }}
          />
          <button type="submit">Search Papers</button>
        </form>
      </div>

      {/* Filter panel */}
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

      {/* Paper results grid */}
      {filteredResults.length > 0 ? (
        <>
          <h2>Search Results for "{selectedQuery}"</h2>
          <PaperCardGrid papers={filteredResults} query={selectedQuery} />
        </>
      ) : (
        searchResults.length > 0 && <p>No results match the selected filters.</p>
      )}
    </div>
  );
};

export default HomePage;
