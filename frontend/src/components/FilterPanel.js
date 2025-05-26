import React from 'react';
import PropTypes from 'prop-types';
import './FilterPanel.css';

const FilterPanel = ({
  dateRange,
  setDateRange,
  relevanceRange,
  setRelevanceRange,
  categories,
  selectedCategories,
  setSelectedCategories,
}) => {
  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  return (
    <div className="filter-panel">
      <h3>検索結果のフィルター</h3>
      
      <div className="filter-section">
        <h4>公開日</h4>
        <div className="range-inputs">
          <input
            type="range"
            min="0"
            max="100"
            value={dateRange[0]}
            onChange={(e) => setDateRange([parseInt(e.target.value), dateRange[1]])}
          />
          <input
            type="range"
            min="0"
            max="100"
            value={dateRange[1]}
            onChange={(e) => setDateRange([dateRange[0], parseInt(e.target.value)])}
          />
          <div className="range-labels">
            <span>{dateRange[0]}ヶ月前</span>
            <span>〜</span>
            <span>{dateRange[1]}ヶ月前</span>
          </div>
        </div>
      </div>

      <div className="filter-section">
        <h4>関連性スコア</h4>
        <div className="range-inputs">
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={relevanceRange[0]}
            onChange={(e) => setRelevanceRange([parseFloat(e.target.value), relevanceRange[1]])}
          />
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={relevanceRange[1]}
            onChange={(e) => setRelevanceRange([relevanceRange[0], parseFloat(e.target.value)])}
          />
          <div className="range-labels">
            <span>{relevanceRange[0].toFixed(2)}</span>
            <span>〜</span>
            <span>{relevanceRange[1].toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="filter-section">
        <h4>カテゴリ</h4>
        <div className="category-filters">
          {categories.map(category => (
            <label key={category} className="category-checkbox">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category)}
                onChange={() => handleCategoryToggle(category)}
              />
              <span>{category}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

FilterPanel.propTypes = {
  dateRange: PropTypes.arrayOf(PropTypes.number).isRequired,
  setDateRange: PropTypes.func.isRequired,
  relevanceRange: PropTypes.arrayOf(PropTypes.number).isRequired,
  setRelevanceRange: PropTypes.func.isRequired,
  categories: PropTypes.arrayOf(PropTypes.string).isRequired,
  selectedCategories: PropTypes.arrayOf(PropTypes.string).isRequired,
  setSelectedCategories: PropTypes.func.isRequired,
};

export default FilterPanel;
