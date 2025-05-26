import React from 'react';
import PropTypes from 'prop-types';
import './QueryTreeVisualizer.css';

const QueryTreeVisualizer = ({ data }) => {
  return (
    <div className="query-tree">
      <div className="query-tree-header">
        <h2>検索クエリツリー</h2>
        <p className="original-query">元のクエリ: {data.name}</p>
      </div>
      <div className="query-nodes">
        {data.children.map((node, index) => (
          <div key={index} className="query-node">
            <div className="query-content">
              <h3>検索クエリ {index + 1}</h3>
              <p className="query-text">{node.name}</p>
              <p className="query-description">{node.description}</p>
              <div className="papers-count">
                関連論文: {node.papers.length}件
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

QueryTreeVisualizer.propTypes = {
  data: PropTypes.shape({
    name: PropTypes.string.isRequired,
    children: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string.isRequired,
        description: PropTypes.string.isRequired,
        papers: PropTypes.array.isRequired,
      })
    ).isRequired,
  }).isRequired,
};

export default QueryTreeVisualizer; 