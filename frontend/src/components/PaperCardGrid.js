import React from 'react';
import PropTypes from 'prop-types';
import './PaperCardGrid.css';

const PaperCardGrid = ({ papers }) => {
  return (
    <div className="paper-card-grid">
      {papers.map((paper, index) => (
        <div key={paper.arxiv_id || index} className="paper-card">
          <h3 className="paper-title">{paper.title}</h3>
          <p className="paper-authors">{paper.authors.join(', ')}</p>
          <p className="paper-date">公開日: {paper.date}</p>
          <div className="paper-relevance">
            <span className="relevance-label">関連性:</span>
            <span className={`relevance-score ${
              paper.relevance_score >= 0.95 ? 'high' : 
              paper.relevance_score >= 0.85 ? 'medium' : 'low'
            }`}>
              {paper.relevance_score.toFixed(2)}
            </span>
          </div>
          <p className="paper-abstract">{paper.abstract}</p>
          <div className="paper-categories">
            {paper.categories.map(category => (
              <span key={category} className="category-tag">{category}</span>
            ))}
          </div>
          <div className="paper-actions">
            <a 
              href={paper.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="paper-link"
            >
              論文を読む
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

PaperCardGrid.propTypes = {
  papers: PropTypes.arrayOf(
    PropTypes.shape({
      arxiv_id: PropTypes.string,
      title: PropTypes.string.isRequired,
      authors: PropTypes.arrayOf(PropTypes.string).isRequired,
      date: PropTypes.string.isRequired,
      abstract: PropTypes.string.isRequired,
      relevance_score: PropTypes.number.isRequired,
      categories: PropTypes.arrayOf(PropTypes.string).isRequired,
      url: PropTypes.string.isRequired,
    })
  ).isRequired,
};

export default PaperCardGrid; 