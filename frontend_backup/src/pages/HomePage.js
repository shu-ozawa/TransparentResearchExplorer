import React, { useState, useEffect, useCallback } from 'react';
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
      setSelectedQuery(keywords); // 選択されたクエリを更新
      const result = await apiService.generateQuery(keywords);
      console.log('Generated queries:', result);

      // Update state with query tree data
      if (result.related_queries && Array.isArray(result.related_queries)) {
        setQueryTreeData({
          name: result.original_query,
          children: result.related_queries.map(q => ({
            name: q.query,
            children: [] // 必要に応じて子ノードを追加
          }))
        });
      }

      // 自動的に論文検索を実行
      await handleQuerySelect(keywords);
    } catch (error) {
      console.error('Error generating query:', error);
      alert(`Failed to generate query: ${error.message}`);
    }
  };

  // Filtering state
  const [dateRange, setDateRange] = useState([0, 100]);
  const [relevanceRange, setRelevanceRange] = useState([0, 5]);
  const categories = ['cs.AI', 'cs.LG', 'stat.ML', 'physics.hep-th'];
  const [selectedCategories, setSelectedCategories] = useState([]);

  const applyFilters = useCallback((results) => {
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
  }, [dateRange, relevanceRange, selectedCategories]);

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
      applyFilters(formattedResults);
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

  useEffect(() => {
    if (searchResults.length > 0) {
      applyFilters(searchResults);
    }
  }, [searchResults, applyFilters]);

  return (
    <div>
      <h1>Transparent Research Explorer</h1>

      {/* 統合された検索フォーム */}
      <QueryInputForm 
        onSubmit={handleKeywordsSubmit}
        initialValue={selectedQuery}
      />

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
