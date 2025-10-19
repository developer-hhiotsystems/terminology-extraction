import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './GraphVisualization.css';

interface GraphNode {
  id: number;
  label: string;
  term: string;
  language: string;
  definition_count: number;
  group?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphEdge {
  id: string;
  source: number | GraphNode;
  target: number | GraphNode;
  type: string;
  weight: number;
  label: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    node_count: number;
    edge_count: number;
    relationship_types: string[];
    avg_confidence: number;
  };
}

interface GraphVisualizationProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  highlightedNodeId?: number | null;
  selectedRelationTypes?: string[];
}

/**
 * GraphVisualization Component
 *
 * Interactive D3.js force-directed graph for term relationships:
 * - Nodes: Glossary terms
 * - Edges: Semantic relationships
 * - Force simulation for layout
 * - Zoom and pan
 * - Drag nodes
 * - Hover tooltips
 * - Relationship type filtering
 * - Node highlighting
 *
 * Based on D3.js v7 force-directed graph
 */
export default function GraphVisualization({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  onEdgeClick,
  highlightedNodeId = null,
  selectedRelationTypes = [],
}: GraphVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<GraphEdge | null>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    // Filter edges by selected relation types
    const filteredEdges = selectedRelationTypes.length > 0
      ? data.edges.filter(e => selectedRelationTypes.includes(e.type))
      : data.edges;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height] as any);

    // Add zoom behavior
    const g = svg.append('g');

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
      .data(Array.from(new Set(filteredEdges.map(d => d.type))))
      .join('marker')
      .attr('id', d => `arrow-${d}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('fill', d => getEdgeColor(d))
      .attr('d', 'M0,-5L10,0L0,5');

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(filteredEdges)
        .id((d: any) => d.id)
        .distance(100)
        .strength(d => (d as GraphEdge).weight))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create links (edges)
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(filteredEdges)
      .join('line')
      .attr('class', 'edge')
      .attr('stroke', d => getEdgeColor(d.type))
      .attr('stroke-width', d => Math.max(1, d.weight * 3))
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', d => `url(#arrow-${d.type})`)
      .on('mouseenter', (_event, d) => setHoveredEdge(d))
      .on('mouseleave', () => setHoveredEdge(null))
      .on('click', (event, d) => {
        event.stopPropagation();
        onEdgeClick?.(d);
      });

    // Create nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    // Node circles
    node.append('circle')
      .attr('r', d => 8 + d.definition_count * 2)
      .attr('fill', d => getNodeColor(d))
      .attr('stroke', d => d.id === highlightedNodeId ? '#ffc107' : '#fff')
      .attr('stroke-width', d => d.id === highlightedNodeId ? 4 : 2)
      .on('mouseenter', (_event, d) => setHoveredNode(d))
      .on('mouseleave', () => setHoveredNode(null))
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeClick?.(d);
      });

    // Node labels
    node.append('text')
      .text(d => d.label)
      .attr('x', 12)
      .attr('y', 4)
      .attr('class', 'node-label')
      .attr('font-size', '11px')
      .attr('fill', '#e0e0e0')
      .attr('pointer-events', 'none');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [data, width, height, highlightedNodeId, selectedRelationTypes]);

  // Get node color based on language or group
  const getNodeColor = (node: GraphNode): string => {
    if (node.language === 'en') return '#4a9eff';
    if (node.language === 'de') return '#ff9800';
    if (node.group) {
      // Color by domain/group
      const colors = ['#4caf50', '#9c27b0', '#e91e63', '#00bcd4', '#ffeb3b'];
      const hash = node.group.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      return colors[hash % colors.length];
    }
    return '#888';
  };

  // Get edge color based on relationship type
  const getEdgeColor = (type: string): string => {
    const colors: Record<string, string> = {
      uses: '#4a9eff',
      measures: '#4caf50',
      part_of: '#9c27b0',
      produces: '#ff9800',
      affects: '#e91e63',
      requires: '#f44336',
      controls: '#00bcd4',
      defines: '#ffeb3b',
      related_to: '#888',
    };
    return colors[type] || '#888';
  };

  return (
    <div className="graph-visualization-container">
      <svg ref={svgRef} className="graph-svg"></svg>

      {/* Hover Tooltip for Nodes */}
      {hoveredNode && (
        <div
          className="graph-tooltip node-tooltip"
          style={{
            position: 'fixed',
            left: '50%',
            top: '20px',
            transform: 'translateX(-50%)',
          }}
        >
          <div className="tooltip-title">{hoveredNode.label}</div>
          <div className="tooltip-content">
            <div>Language: {hoveredNode.language.toUpperCase()}</div>
            <div>Definitions: {hoveredNode.definition_count}</div>
            {hoveredNode.group && <div>Domain: {hoveredNode.group}</div>}
          </div>
        </div>
      )}

      {/* Hover Tooltip for Edges */}
      {hoveredEdge && (
        <div
          className="graph-tooltip edge-tooltip"
          style={{
            position: 'fixed',
            left: '50%',
            top: '70px',
            transform: 'translateX(-50%)',
          }}
        >
          <div className="tooltip-title">{hoveredEdge.label}</div>
          <div className="tooltip-content">
            <div>Type: {hoveredEdge.type}</div>
            <div>Confidence: {(hoveredEdge.weight * 100).toFixed(0)}%</div>
          </div>
        </div>
      )}

      {/* Stats Display */}
      <div className="graph-stats">
        <div className="stat-item">
          <span className="stat-label">Nodes:</span>
          <span className="stat-value">{data.stats.node_count}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Relationships:</span>
          <span className="stat-value">{data.stats.edge_count}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Avg Confidence:</span>
          <span className="stat-value">{(data.stats.avg_confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Legend */}
      <div className="graph-legend">
        <div className="legend-title">Relationship Types</div>
        {data.stats.relationship_types.map(type => (
          <div key={type} className="legend-item">
            <div
              className="legend-color"
              style={{ backgroundColor: getEdgeColor(type) }}
            ></div>
            <span className="legend-label">{type.replace('_', ' ')}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
