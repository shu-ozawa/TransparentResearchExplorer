import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import * as d3 from 'd3';

const QueryTreeVisualizer = ({ data, onQuerySelect }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.children) return;

    // Set up dimensions and margins
    const margin = { top: 20, right: 90, bottom: 30, left: 90 };
    const width = 800 - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;

    // Remove any existing SVG
    d3.select(svgRef.current).selectAll('*').remove();

    // Create the SVG container
    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create the tree layout
    const treemap = d3.tree().size([width, height]);

    // Hierarchy from data
    const root = d3.hierarchy(data);
    treemap(root);

    // Links
    svg.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkHorizontal()
        .x(d => d.y)
        .y(d => d.x))
      .attr('fill', 'none')
      .attr('stroke', '#ccc');

    // Nodes
    const node = svg.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .on('click', (event, d) => {
        if (d.data.name && onQuerySelect) {
          onQuerySelect(d.data.name);
        }
      });

    node.append('circle')
      .attr('r', 5)
      .attr('fill', '#999');

    const text = node.append('text')
      .attr('dy', '.35em')
      .attr('x', d => d.children ? -10 : 10)
      .style('text-anchor', d => d.children ? 'end' : 'start')
      .style('cursor', 'pointer')
      .style('fill', '#007bff')
      .text(d => d.data.name);

    // Add hover effect to text
    text.on('mouseover', function() {
      d3.select(this).style('font-weight', 'bold');
    })
    .on('mouseout', function() {
      d3.select(this).style('font-weight', 'normal');
    });

    // Add zoom capability
    const zoom = d3.zoom()
      .scaleExtent([0.5, 2])
      .on('zoom', (event) => {
        svg.attr('transform', event.transform);
      });

    d3.select(svgRef.current)
      .call(zoom)
      .call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(0.8));
  }, [data, onQuerySelect]);

  return (
    <div>
      <h2>Query Tree Visualization</h2>
      {onQuerySelect && <p>Click on a query node to search papers with that query</p>}
      <svg ref={svgRef}></svg>
    </div>
  );
};

QueryTreeVisualizer.propTypes = {
  data: PropTypes.shape({
    name: PropTypes.string.isRequired,
    children: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string.isRequired,
    })),
  }),
  onQuerySelect: PropTypes.func,
};

export default QueryTreeVisualizer;
