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
  // 進捗インジケーター用
  const [progress, setProgress] = useState({
    phase: '', // '', 'generating', 'searching', 'done'
    current: 0,
    total: 0,
    queries: [] // [{query, status: 'pending'|'searching'|'done'|'error'}]
  });

  const handlePaperNodeClick = (paperData) => {
    setSelectedPaperForSidebar(paperData);
    setIsSidebarOpen(true);
  };

  const handleCloseSidebar = () => {
    setIsSidebarOpen(false);
    // Optionally delay setting paper to null for animation:
    // setTimeout(() => setSelectedPaperForSidebar(null), 300);
  };

  const handleSearch = async (query, maxResults = 5, maxQueries = 5) => {
    setLoading(true);
    setError(null);
    setResearchData(null);
    setSelectedQuery(query);
    setProgress({ phase: 'generating', current: 0, total: 0, queries: [] });
    let tempData = {
      original_query: query,
      research_goal: '',
      query_nodes: [],
      total_papers: 0,
      total_unique_papers: 0
    };
    const uniqueArxivIds = new Set();
    try {
      await apiService.searchResearchTreeStream(
        query,
        (data) => {
          if (data.type === 'queries') {
            tempData.research_goal = data.research_goal;
            tempData.query_nodes = [];
            setResearchData({ ...tempData });
            setProgress({
              phase: 'searching',
              current: 0,
              total: data.queries.length,
              queries: data.queries.map(q => ({ query: q.query, status: 'pending' }))
            });
          } else if (data.type === 'papers') {
            // クエリごとの論文リストを追加
            tempData.query_nodes.push({
              query: data.query,
              description: data.description,
              papers: data.papers,
              paper_count: data.papers.length
            });
            // 論文数集計
            tempData.total_papers += data.papers.length;
            data.papers.forEach(p => uniqueArxivIds.add(p.arxiv_id));
            tempData.total_unique_papers = uniqueArxivIds.size;
            setResearchData({ ...tempData });
            // 進捗更新
            setProgress(prev => {
              const idx = prev.queries.findIndex(q => q.query === data.query);
              if (idx !== -1) {
                const newQueries = [...prev.queries];
                newQueries[idx] = {
                  ...newQueries[idx],
                  status: data.error ? 'error' : 'done'
                };
                return {
                  ...prev,
                  current: prev.current + 1,
                  queries: newQueries,
                  phase: prev.current + 1 === prev.total ? 'done' : prev.phase
                };
              }
              return prev;
            });
          }
        },
        maxResults,
        maxQueries
      );
    } catch (err) {
      setError(err.message || '検索中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  // Removed Filtering state (dateRange, relevanceRange, selectedCategories)
  // Removed applyFilters function
  // Removed useEffect for applyFilters
  // Removed useMemo for categories

  // 進捗インジケーターUI
  const renderProgress = () => {
    if (progress.phase === 'generating') {
      return <div className="progress-indicator">Generating queries...</div>;
    }
    if (progress.phase === 'searching') {
      return (
        <div className="progress-indicator">
          Searching: {progress.current} / {progress.total}
          <ul style={{margin: '0.5em 0 0 1.5em', padding: 0}}>
            {progress.queries.map((q, i) => (
              <li key={i} style={{color: q.status === 'done' ? 'green' : q.status === 'error' ? 'red' : 'black'}}>
                {q.query} : {q.status === 'pending' ? 'Pending' : q.status === 'searching' ? 'Searching' : q.status === 'done' ? 'Done' : 'Error'}
              </li>
            ))}
          </ul>
        </div>
      );
    }
    if (progress.phase === 'done' && progress.total > 0) {
      return <div className="progress-indicator">All searches completed</div>;
    }
    return null;
  };

  return (
    <div className="home-page">
      <h1>Transparent Research Explorer</h1>

      <QueryInputForm 
        onSubmit={handleSearch}
        initialValue={selectedQuery} 
        loading={loading}
      />

      {renderProgress()}

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
