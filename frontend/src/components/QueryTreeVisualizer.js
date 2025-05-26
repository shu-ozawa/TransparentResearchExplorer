import React, { useState, useEffect, useRef, useMemo } from 'react';
import PropTypes from 'prop-types';
// Assuming QueryTreeVisualizer.css is not used anymore or its content is in style.css
// If specific styles from QueryTreeVisualizer.css are needed, ensure they are migrated or the import retained.
// For now, we rely on style.css as per instructions.
// import './QueryTreeVisualizer.css';

const QueryTreeVisualizer = ({ researchData, onPaperNodeClick }) => {
  const [connections, setConnections] = useState([]);
  const svgRef = useRef(null);
  const [activeNodeIds, setActiveNodeIds] = useState([]);
  const [activeLineIds, setActiveLineIds] = useState([]);

  // Extract unique papers and calculate stats if researchData is available
  const {
    uniquePapers,
    totalQueries,
    totalUniquePapers,
    totalPapersReferenced,
    averagePapersPerQuery
  } = useMemo(() => {
    if (!researchData || !researchData.query_nodes) {
      return {
        uniquePapers: [],
        totalQueries: 0,
        totalUniquePapers: 0,
        totalPapersReferenced: 0,
        averagePapersPerQuery: 0,
      };
    }

    const papersMap = new Map();
    let papersReferencedCount = 0;
    researchData.query_nodes.forEach(node => {
      papersReferencedCount += node.papers.length;
      node.papers.forEach(paper => {
        if (!papersMap.has(paper.arxiv_id)) {
          papersMap.set(paper.arxiv_id, paper);
        }
      });
    });
    const currentUniquePapers = Array.from(papersMap.values());
    const currentTotalQueries = researchData.query_nodes.length;
    const currentTotalUniquePapers = currentUniquePapers.length;
    const currentAveragePapersPerQuery = currentTotalQueries > 0 ? currentTotalUniquePapers / currentTotalQueries : 0;

    return {
      uniquePapers: currentUniquePapers,
      totalQueries: currentTotalQueries,
      totalUniquePapers: currentTotalUniquePapers,
      totalPapersReferenced: papersReferencedCount,
      averagePapersPerQuery: currentAveragePapersPerQuery,
    };
  }, [researchData]);

  const getElementCenter = (elementId, svgContainerRef) => {
    const element = document.getElementById(elementId);
    const svgElement = svgContainerRef.current;
    if (element && svgElement) {
      const elementRect = element.getBoundingClientRect();
      const svgRect = svgElement.getBoundingClientRect();

      const x = elementRect.left + elementRect.width / 2 - svgRect.left;
      const y = elementRect.top + elementRect.height / 2 - svgRect.top;
      return { x, y };
    }
    return null;
  };

  useEffect(() => {
    if (!researchData) return; // Guard against null researchData

    const newConnections = [];
    if (!svgRef.current) return;

    const goalNodeDomId = 'research-goal-node'; // Consistent ID for the goal node element
    const goalNodeCenter = getElementCenter(goalNodeDomId, svgRef);

    if (goalNodeCenter) {
      researchData.query_nodes.forEach((queryNode, index) => {
        const queryNodeDomId = `query-node-${index}`;
        const queryNodeCenter = getElementCenter(queryNodeDomId, svgRef);

        if (queryNodeCenter) {
          newConnections.push({
            id: `line-${goalNodeDomId}-to-${queryNodeDomId}`,
            startX: goalNodeCenter.x,
            startY: goalNodeCenter.y,
            endX: queryNodeCenter.x,
            endY: queryNodeCenter.y,
            startNodeId: goalNodeDomId,
            endNodeId: queryNodeDomId,
          });

          queryNode.papers.forEach((paper) => {
            const paperNodeDomId = `paper-${paper.arxiv_id}`;
            const paperNodeCenter = getElementCenter(paperNodeDomId, svgRef);

            if (paperNodeCenter) {
              newConnections.push({
                id: `line-${queryNodeDomId}-to-${paperNodeDomId}`,
                startX: queryNodeCenter.x,
                startY: queryNodeCenter.y,
                endX: paperNodeCenter.x,
                endY: paperNodeCenter.y,
                startNodeId: queryNodeDomId,
                endNodeId: paperNodeDomId,
              });
            }
          });
        }
      });
    }
    setConnections(newConnections);
  }, [researchData, uniquePapers]); // uniquePapers is now derived from researchData in useMemo

  const handleNodeMouseEnter = (hoveredNodeId, type) => {
    const currentNodeIds = [hoveredNodeId];
    const currentLineIds = [];

    connections.forEach(conn => {
      if (type === 'goal') {
        if (conn.startNodeId === hoveredNodeId) {
          currentLineIds.push(conn.id);
          currentNodeIds.push(conn.endNodeId);
        }
      } else if (type === 'query') {
        if (conn.startNodeId === hoveredNodeId) {
          currentLineIds.push(conn.id);
          currentNodeIds.push(conn.endNodeId);
        } else if (conn.endNodeId === hoveredNodeId) {
          currentLineIds.push(conn.id);
          currentNodeIds.push(conn.startNodeId);
        }
      } else if (type === 'paper') {
        if (conn.endNodeId === hoveredNodeId) {
          currentLineIds.push(conn.id);
          currentNodeIds.push(conn.startNodeId);
        }
      }
    });
    setActiveNodeIds(currentNodeIds);
    setActiveLineIds(currentLineIds);
  };

  const handleNodeMouseLeave = () => {
    setActiveNodeIds([]);
    setActiveLineIds([]);
  };

  const goalNodeDomId = 'research-goal-node';

  if (!researchData) {
    return null; // Or some loading/empty state
  }

  return (
    <>
      {/* Statistical Overview */}
      <div className="stats-overview">
        <h3 className="stats-title">Research Network Overview</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{totalQueries}</div>
            <div className="stat-label">AI Queries</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{totalUniquePapers}</div>
            <div className="stat-label">Unique Papers</div>
          </div>
           <div className="stat-card">
            <div className="stat-number">{totalPapersReferenced}</div>
            <div className="stat-label">Total Paper Citations</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{averagePapersPerQuery.toFixed(1)}</div>
            <div className="stat-label">Avg. Unique Papers per Query</div>
          </div>
        </div>
      </div>

      {/* Network Graph */}
      <div className="network-graph">
        <svg
          ref={svgRef}
          className="network-svg"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 1,
            pointerEvents: 'none',
          }}
        >
          {connections.map(conn => {
            // Simple vertical curve for goal-to-query and query-to-paper
            // Adjust the multiplier (e.g., 0.3, 0.4, 0.5) to change curve intensity
            // A larger multiplier means the control points are further along the line, making the curve "gentler"
            // A smaller multiplier makes it "sharper" or more bowed if control points are offset from the line.
            // For now, we use a simple vertical offset for control points.

            let cp1x, cp1y, cp2x, cp2y;
            const yDiff = conn.endY - conn.startY;
            const xDiff = conn.endX - conn.startX;

            // General approach: control points are offset vertically from start/end points
            // This creates a gentle "S" curve for vertical connections or an arc for others.
            cp1x = conn.startX;
            cp1y = conn.startY + yDiff * 0.33; // First control point pulls "down" from start
            cp2x = conn.endX;
            cp2y = conn.endY - yDiff * 0.33;   // Second control point pulls "up" from end
            
            // If the connection is more horizontal than vertical, adjust control points to bend horizontally
            if (Math.abs(xDiff) > Math.abs(yDiff)) {
                cp1x = conn.startX + xDiff * 0.33;
                cp1y = conn.startY;
                cp2x = conn.endX - xDiff * 0.33;
                cp2y = conn.endY;
            }


            const pathData = `M ${conn.startX} ${conn.startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${conn.endX} ${conn.endY}`;

            return (
              <path
                key={conn.id}
                d={pathData}
                className={`connection-line ${activeLineIds.includes(conn.id) ? 'active' : ''}`}
                fill="none" // Important for paths if not already in CSS
              />
            );
          })}
        </svg>

        {/* Research Goal Node */}
        <div
          id={goalNodeDomId}
          className={`network-node human-input ${activeNodeIds.includes(goalNodeDomId) ? 'active' : ''}`}
          onMouseEnter={() => handleNodeMouseEnter(goalNodeDomId, 'goal')}
          onMouseLeave={handleNodeMouseLeave}
        >
          <div className="input-title">{researchData.research_goal}</div>
        </div>

        {/* Query Nodes */}
        <div className="query-nodes-container" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '32px', marginTop: '50px', marginBottom: '50px' }}>
          {researchData.query_nodes.map((node, index) => {
            const queryNodeDomId = `query-node-${index}`;
            return (
              <div
                key={index}
                id={queryNodeDomId}
                className={`network-node query-node query${index + 1} ${activeNodeIds.includes(queryNodeDomId) ? 'active' : ''}`}
                style={{ position: 'static', minWidth: 280, maxWidth: 400, flex: '1 1 320px' }}
                onMouseEnter={() => handleNodeMouseEnter(queryNodeDomId, 'query')}
                onMouseLeave={handleNodeMouseLeave}
              >
                <div className="query-title">{node.query}</div>
                <p className="query-text">{node.description}</p>
              </div>
            );
          })}
        </div>

        {/* Paper Nodes */}
        <div className="paper-nodes-container" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '20px' }}>
          {uniquePapers.map((paper, index) => {
            const paperNodeDomId = `paper-${paper.arxiv_id}`;
            return (
              <div
                key={paper.arxiv_id}
                id={paperNodeDomId}
                data-id={paper.arxiv_id}
                className={`network-node paper-node paper${index + 1} ${activeNodeIds.includes(paperNodeDomId) ? 'active' : ''}`}
                style={{ position: 'static', minWidth: 280, maxWidth: 400, flex: '1 1 320px' }}
                onMouseEnter={() => handleNodeMouseEnter(paperNodeDomId, 'paper')}
                onMouseLeave={handleNodeMouseLeave}
                onClick={() => onPaperNodeClick && onPaperNodeClick(paper)}
              >
                <div className="paper-title">{paper.title}</div>
                <div className="paper-authors">{paper.authors.join(', ')}</div>
                <div className="paper-footer">
                  <span className="paper-date">{paper.published_date}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="legend">
        <h3 className="legend-title">Legend</h3>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color input"></div>
            <span className="legend-text">Research Goal / Human Input</span>
          </div>
          <div className="legend-item">
            <div className="legend-color query"></div>
            <span className="legend-text">AI-Generated Query</span>
          </div>
          <div className="legend-item">
            <div className="legend-color paper"></div>
            <span className="legend-text">Research Paper</span>
          </div>
        </div>
      </div>
    </>
  );
};

QueryTreeVisualizer.propTypes = {
  researchData: PropTypes.shape({
    research_goal: PropTypes.string.isRequired,
    query_nodes: PropTypes.arrayOf(
      PropTypes.shape({
        query: PropTypes.string.isRequired,
        description: PropTypes.string.isRequired,
        papers: PropTypes.arrayOf(
          PropTypes.shape({
            arxiv_id: PropTypes.string.isRequired,
            title: PropTypes.string.isRequired,
            authors: PropTypes.arrayOf(PropTypes.string).isRequired,
            published_date: PropTypes.string.isRequired,
            categories: PropTypes.arrayOf(PropTypes.string),
            relevance_score: PropTypes.number,
            url: PropTypes.string,
            abstract: PropTypes.string,
          })
        ).isRequired,
      })
    ).isRequired,
  }), // researchData can be null initially
  onPaperNodeClick: PropTypes.func,
};

export default QueryTreeVisualizer;