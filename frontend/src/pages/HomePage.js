import React from 'react';
import ExampleComponent from '../components/ExampleComponent';
import QueryInputForm from '../components/QueryInputForm';

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
    </div>
  );
};

export default HomePage;
