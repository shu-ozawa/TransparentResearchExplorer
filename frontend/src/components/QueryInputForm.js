import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './QueryInputForm.css';

const QueryInputForm = ({ onSubmit, initialValue, loading }) => {
  const [keywords, setKeywords] = useState(initialValue || '');
  const [maxResults, setMaxResults] = useState(5);
  const [maxQueries, setMaxQueries] = useState(5);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    if (initialValue) {
      setKeywords(initialValue);
    }
  }, [initialValue]);

  const handleChange = (e) => {
    setKeywords(e.target.value);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (onSubmit && keywords.trim()) {
      onSubmit(keywords.trim(), maxResults, maxQueries);
    }
  };

  return (
    <form className="query-input-form" onSubmit={handleFormSubmit} style={{ background: '#f7f1ea', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(120, 72, 0, 0.06)' }}>
      <div className="main-input">
        <label htmlFor="keywords" style={{ color: '#7a5c2e', fontWeight: 'bold' }}>Research Keyword / Topic:</label>
        <input
          type="text"
          id="keywords"
          value={keywords}
          onChange={handleChange}
          required
          placeholder="Enter keyword or research topic"
          disabled={loading}
          style={{ border: '1.5px solid #bfa16a', borderRadius: 8, padding: '8px 12px', background: '#f7f1ea', color: '#7a5c2e' }}
        />
      </div>

      <div className="advanced-settings">
        <button
          type="button"
          className="toggle-advanced"
          onClick={() => setShowAdvanced(!showAdvanced)}
          disabled={loading}
          style={{ color: '#7a5c2e', background: '#f7e7d3', border: '1px solid #bfa16a', borderRadius: 8 }}
        >
          {showAdvanced ? 'Hide Advanced Settings ▼' : 'Show Advanced Settings ▶'}
        </button>

        {showAdvanced && (
          <div className="advanced-options">
            <div className="option-group">
              <label htmlFor="maxResults" style={{ color: '#7a5c2e' }}>Max papers per query:</label>
              <input
                type="number"
                id="maxResults"
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                min="1"
                max="20"
                disabled={loading}
                style={{ border: '1.5px solid #bfa16a', borderRadius: 8, padding: '4px 8px', background: '#f7f1ea', color: '#7a5c2e' }}
              />
            </div>

            <div className="option-group">
              <label htmlFor="maxQueries" style={{ color: '#7a5c2e' }}>Number of queries to generate:</label>
              <input
                type="number"
                id="maxQueries"
                value={maxQueries}
                onChange={(e) => setMaxQueries(Number(e.target.value))}
                min="1"
                max="10"
                disabled={loading}
                style={{ border: '1.5px solid #bfa16a', borderRadius: 8, padding: '4px 8px', background: '#f7f1ea', color: '#7a5c2e' }}
              />
            </div>
          </div>
        )}
      </div>

      <button 
        type="submit" 
        className={`submit-button ${loading ? 'loading' : ''}`}
        disabled={loading}
        style={{ background: '#bfa16a', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', fontWeight: 'bold', fontSize: '1.1em', marginTop: 12 }}
      >
        {loading ? 'Searching...' : 'Start Search'}
      </button>
    </form>
  );
};

QueryInputForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  initialValue: PropTypes.string,
  loading: PropTypes.bool
};

export default QueryInputForm;
