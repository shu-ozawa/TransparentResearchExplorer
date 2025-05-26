import React, { useState, useEffect, useCallback, useMemo } from 'react';
import QueryInputForm from '../components/QueryInputForm';
import PaperCardGrid from '../components/PaperCardGrid';
import apiService from '../services/apiService';
import QueryTreeVisualizer from '../components/QueryTreeVisualizer';
import FilterPanel from '../components/FilterPanel';

const HomePage = () => {
  const [researchData, setResearchData] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [selectedQuery, setSelectedQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
          queryContext: node.description,
          relevanceScore: paper.relevance_score,
          date: new Date(paper.published_date).toLocaleDateString()
        }))
      );

      setSearchResults(allPapers);
      setFilteredResults(allPapers);
      setSelectedQuery(query);
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

      {/* 検索フォーム */}
      <QueryInputForm 
        onSubmit={handleSearch}
        initialValue={selectedQuery}
        loading={loading}
      />

      {/* エラー表示 */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 研究目標の表示 */}
      {researchData?.research_goal && (
        <div className="research-goal">
          <h2>研究目標:</h2>
          <p>{researchData.research_goal}</p>
        </div>
      )}

      {/* Query Tree Visualizer */}
      {researchData?.query_nodes && (
        <QueryTreeVisualizer
          data={{
            name: selectedQuery,
            children: researchData.query_nodes.map(node => ({
              name: node.query,
              description: node.description,
              papers: node.papers
            }))
          }}
        />
      )}

      {/* フィルターパネル */}
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

      {/* 検索結果の表示 */}
      {loading ? (
        <div className="loading">検索中...</div>
      ) : (
        <>
          {filteredResults.length > 0 ? (
            <>
              <h2>検索結果: {filteredResults.length}件</h2>
              <PaperCardGrid papers={filteredResults} />
            </>
          ) : (
            searchResults.length > 0 && <p>選択されたフィルタに一致する結果がありません。</p>
          )}
        </>
      )}
    </div>
  );
};

export default HomePage;
