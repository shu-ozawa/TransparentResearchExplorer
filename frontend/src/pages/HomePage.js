import React, { useState } from 'react';
import ExampleComponent from '../components/ExampleComponent';
import QueryInputForm from '../components/QueryInputForm';
import { PaperCardWithDummyData } from '../components/PaperCard';
import apiService from '../services/apiService';
import QueryTreeVisualizer from '../components/QueryTreeVisualizer';

const handleKeywordsSubmit = async (keywords) => {
  try {
    const result = await apiService.generateQuery(keywords);
    console.log('Generated queries:', result);
    alert(`Original Query: ${result.original_query}\n\nRelated Queries:\n${result.related_queries.map(q => q.query).join('\n')}`);
  } catch (error) {
    console.error('Error generating query:', error);
    alert(`Failed to generate query: ${error.message}`);
  }
};

const HomePage = () => {
  const [queryTreeData, setQueryTreeData] = useState(null);

  const loadQueryTreeData = async () => {
    try {
      const data = await apiService.fetchQueryTreeData();
      setQueryTreeData(data);
    } catch (error) {
      console.error('Error fetching query tree data:', error);
    }
  };

  return (
    <div>
      <h1>Transparent Research Explorer</h1>
      <QueryInputForm onSubmit={handleKeywordsSubmit} />
      <ExampleComponent />

      {/* Testing the PaperCard component */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
        <PaperCardWithDummyData />
      </div>

      {/* Query Tree Visualizer */}
      <button onClick={loadQueryTreeData}>Load Query Tree</button>
      {queryTreeData && <QueryTreeVisualizer data={queryTreeData} />}
    </div>
  );
};

export default HomePage;
