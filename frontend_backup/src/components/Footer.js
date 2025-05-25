import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      &copy; {new Date().getFullYear()} Transparent Research Explorer
    </footer>
  );
};

export default Footer;
