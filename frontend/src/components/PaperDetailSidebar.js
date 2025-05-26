import React from 'react';
import PropTypes from 'prop-types';

// Assuming styles are primarily from style.css, imported globally or in a parent component.
// If not, import specific CSS here: import './PaperDetailSidebar.css';

const PaperDetailSidebar = ({ paper, isOpen, onClose }) => {
  if (!isOpen || !paper) {
    return null;
  }

  const {
    title,
    authors,
    published_date,
    abstract,
    arxiv_id,
    categories,
    relevance_score,
    url,
  } = paper;

  const arxivLink = url || `https://arxiv.org/abs/${arxiv_id}`;

  // Simple date formatting, can be improved with a library if needed
  const formattedDate = new Date(published_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-content">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>

        <div className="paper-detail-header">
          <h3 className="detail-title">{title}</h3>
        </div>

        <div className="detail-metadata">
          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="metadata-label">Authors</span>
              <span className="metadata-value">{authors && authors.join(', ')}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Published Date</span>
              <span className="metadata-value">{formattedDate}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Categories</span>
              <span className="metadata-value">{categories && categories.join(', ')}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Relevance Score</span>
              <span className="metadata-value">{relevance_score !== undefined ? relevance_score.toFixed(3) : 'N/A'}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">ArXiv Link</span>
              <span className="metadata-value">
                <a href={arxivLink} target="_blank" rel="noopener noreferrer">
                  {arxivLink}
                </a>
              </span>
            </div>
            {/* Add other metadata items here if needed */}
          </div>
        </div>

        {abstract && (
          <div className="abstract-section">
            <h4 className="abstract-header">Abstract</h4>
            <p className="abstract-text">{abstract}</p>
          </div>
        )}
        
        {/* Placeholder for AI Analysis if it's part of the paper object or fetched separately */}
        {/* <div className="ai-analysis">
          <h4 className="analysis-header">AI Analysis</h4>
          <p className="analysis-text">...</p>
        </div> */}
      </div>
    </div>
  );
};

PaperDetailSidebar.propTypes = {
  paper: PropTypes.shape({
    title: PropTypes.string,
    authors: PropTypes.arrayOf(PropTypes.string),
    published_date: PropTypes.string, // Assuming ISO string date
    abstract: PropTypes.string,
    arxiv_id: PropTypes.string,
    categories: PropTypes.arrayOf(PropTypes.string),
    relevance_score: PropTypes.number,
    url: PropTypes.string,
  }),
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default PaperDetailSidebar;
