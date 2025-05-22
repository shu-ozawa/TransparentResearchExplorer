import React, { useState } from 'react';
import ExampleComponent from '../components/ExampleComponent';
import QueryInputForm from '../components/QueryInputForm';
import { PaperCardWithDummyData } from '../components/PaperCard';
import apiService from '../services/apiService';

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
  return (
    <div>
      <h1>Transparent Research Explorer</h1>
      <QueryInputForm onSubmit={handleKeywordsSubmit} />
      <ExampleComponent />

      {/* Testing the PaperCard component */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
        <PaperCardWithDummyData />
      </div>
    </div>
  );
};

export default HomePage;
