import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <h1>Transparent Research Explorer</h1>
      <nav>
        <Link to="/">ホーム</Link>
        {/* 必要に応じて他のナビゲーションリンクを追加できます */}
      </nav>
    </header>
  );
};

export default Header;
