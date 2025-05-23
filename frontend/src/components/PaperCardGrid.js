import React from 'react';
import PropTypes from 'prop-types';
import PaperCard from './PaperCard';

const PaperCardGrid = ({ papers, query }) => {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
      {papers.map((paper, index) => (
        <PaperCard key={index} paper={paper} query={query} />
      ))}
    </div>
  );
};

PaperCardGrid.propTypes = {
  papers: PropTypes.arrayOf(PropTypes.shape({
    title: PropTypes.string.isRequired,
    authors: PropTypes.arrayOf(PropTypes.string).isRequired,
    date: PropTypes.string.isRequired,
    abstract: PropTypes.string.isRequired,
    relevanceScore: PropTypes.number,
    categories: PropTypes.arrayOf(PropTypes.string),
  })).isRequired,
  query: PropTypes.string,
};

export default PaperCardGrid;
