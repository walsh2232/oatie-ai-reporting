import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="App-header">
      <div className="header-content">
        <div className="logo-section">
          <Link to="/" className="logo">
            🥣 Oatie
          </Link>
          <span className="tagline">AI-Powered Oracle BI Publisher Assistant</span>
        </div>
        <nav className="nav">
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link 
            to="/reports" 
            className={`nav-link ${isActive('/reports') ? 'active' : ''}`}
          >
            Reports
          </Link>
          <Link 
            to="/ai-assistant" 
            className={`nav-link ${isActive('/ai-assistant') ? 'active' : ''}`}
          >
            AI Assistant
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;