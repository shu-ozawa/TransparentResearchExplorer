import React from 'react';
import './App.css';
import { AppProvider } from './contexts/AppContext';
import HomePage from './pages/HomePage';

function App() {
  return (
    <AppProvider>
      <div className="App">
        <HomePage />
      </div>
    </AppProvider>
  );
}

export default App;
