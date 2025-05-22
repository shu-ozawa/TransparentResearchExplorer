import React from 'react';
import './App.css';
import { AppProvider } from './contexts/AppContext';
import Header from './components/Header';
import MainContent from './components/MainContent';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';

function App() {
  return (
    <AppProvider>
      <div className="App">
        <Header />
        <MainContent>
          <HomePage />
        </MainContent>
        <Footer />
      </div>
    </AppProvider>
  );
}

export default App;
