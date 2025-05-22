import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './QueryInputForm.css';

const QueryInputForm = ({ onSubmit }) => {
  const [initialKeywords, setInitialKeywords] = useState('');

  const handleChange = (e) => {
    setInitialKeywords(e.target.value);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(initialKeywords.trim());
    }
  };

  return (
    <form className="query-input-form" onSubmit={handleFormSubmit}>
      <div>
        <label htmlFor="initial-keywords">Initial Keywords / Research Theme:</label>
        <input
          type="text"
          id="initial-keywords"
          value={initialKeywords}
          onChange={handleChange}
          required
          placeholder="Enter keywords or research theme"
        />
      </div>
      <button type="submit">Start Research</button>
    </form>
  );
};

QueryInputForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
};

export default QueryInputForm;
