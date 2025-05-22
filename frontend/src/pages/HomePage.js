import React from 'react';
import ExampleComponent from '../components/ExampleComponent';
import QueryInputForm from '../components/QueryInputForm';
import { PaperCardWithDummyData } from '../components/PaperCard';

const handleKeywordsSubmit = (keywords) => {
  console.log('Initial keywords submitted:', keywords);
  // Here you would add logic to start the research process
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
