import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { AppProvider } from './contexts/AppContext';
import Header from './components/Header';
import MainContent from './components/MainContent';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';

function App() {
  return (
    <Router>
      <AppProvider>
        <div className="App">
          <Header />
          <MainContent>
            <Routes>
              <Route path="/" element={<HomePage />} />
              {/* 必要に応じて他のルートを追加できます */}
            </Routes>
          </MainContent>
          <Footer />
        </div>
      </AppProvider>
    </Router>
  );
}

export default App;
