import React from 'react';
import { Slider, TextField, FormControlLabel, Checkbox } from '@mui/material';

const FilterPanel = ({ dateRange, setDateRange, relevanceRange, setRelevanceRange, categories, selectedCategories, setSelectedCategories }) => {
  const handleCategoryChange = (event) => {
    const value = event.target.value;
    if (selectedCategories.includes(value)) {
      setSelectedCategories(selectedCategories.filter((category) => category !== value));
    } else {
      setSelectedCategories([...selectedCategories, value]);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', marginBottom: '20px' }}>
      <h3>Filter Results</h3>

      {/* Date Range Filter */}
      <div>
        <p>Date Range:</p>
        <Slider
          value={dateRange}
          onChange={(event, newValue) => setDateRange(newValue)}
          valueLabelDisplay="auto"
          min={0}
          max={100} // Assuming date range in months from now (customize as needed)
        />
      </div>

      {/* Relevance Score Filter */}
      <div>
        <p>Relevance Score:</p>
        <Slider
          value={relevanceRange}
          onChange={(event, newValue) => setRelevanceRange(newValue)}
          valueLabelDisplay="auto"
          min={0}
          max={5}
          step={1}
        />
      </div>

      {/* Category Filter */}
      <div>
        <p>Categories:</p>
        {categories.map((category, index) => (
          <FormControlLabel
            key={index}
            control={<Checkbox checked={selectedCategories.includes(category)} onChange={handleCategoryChange} value={category} />}
            label={category}
          />
        ))}
      </div>
    </div>
  );
};

export default FilterPanel;
