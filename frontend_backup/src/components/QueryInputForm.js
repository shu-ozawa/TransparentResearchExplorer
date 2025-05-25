import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './QueryInputForm.css';

const QueryInputForm = ({ onSubmit, initialValue }) => {
  const [keywords, setKeywords] = useState(initialValue || '');

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
      onSubmit(keywords.trim());
    }
  };

  return (
    <form className="query-input-form" onSubmit={handleFormSubmit}>
      <div>
        <label htmlFor="keywords">研究キーワード / テーマ:</label>
        <input
          type="text"
          id="keywords"
          value={keywords}
          onChange={handleChange}
          required
          placeholder="キーワードまたは研究テーマを入力"
        />
      </div>
      <button type="submit">検索開始</button>
    </form>
  );
};

QueryInputForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  initialValue: PropTypes.string
};

export default QueryInputForm;
