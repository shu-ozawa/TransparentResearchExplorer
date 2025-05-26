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
    <form className="query-input-form" onSubmit={handleFormSubmit}>
      <div className="main-input">
        <label htmlFor="keywords">研究キーワード / テーマ:</label>
        <input
          type="text"
          id="keywords"
          value={keywords}
          onChange={handleChange}
          required
          placeholder="キーワードまたは研究テーマを入力"
          disabled={loading}
        />
      </div>

      <div className="advanced-settings">
        <button
          type="button"
          className="toggle-advanced"
          onClick={() => setShowAdvanced(!showAdvanced)}
          disabled={loading}
        >
          {showAdvanced ? '詳細設定を隠す ▼' : '詳細設定を表示 ▶'}
        </button>

        {showAdvanced && (
          <div className="advanced-options">
            <div className="option-group">
              <label htmlFor="maxResults">1つのクエリあたりの最大論文数:</label>
              <input
                type="number"
                id="maxResults"
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                min="1"
                max="20"
                disabled={loading}
              />
            </div>

            <div className="option-group">
              <label htmlFor="maxQueries">生成する検索クエリの数:</label>
              <input
                type="number"
                id="maxQueries"
                value={maxQueries}
                onChange={(e) => setMaxQueries(Number(e.target.value))}
                min="1"
                max="10"
                disabled={loading}
              />
            </div>
          </div>
        )}
      </div>

      <button 
        type="submit" 
        className={`submit-button ${loading ? 'loading' : ''}`}
        disabled={loading}
      >
        {loading ? '検索中...' : '検索開始'}
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
