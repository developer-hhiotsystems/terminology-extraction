import { useState, useEffect } from 'react';
import GraphVisualization from './GraphVisualization';
import apiClient from '../api/client';
import './RelationshipExplorer.css';

// Types are inferred from API response - matches GraphVisualization component expectations
type GraphNode = {
  id: number;
  label: string;
  term: string;
  language: string;
  definition_count: number;
  group?: string;
};

type GraphEdge = {
  id: string;
  source: number | GraphNode; // D3.js modifies this during simulation
  target: number | GraphNode; // D3.js modifies this during simulation
  type: string;
  weight: number;
  label: string;
};

type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    node_count: number;
    edge_count: number;
    relationship_types: string[];
    avg_confidence: number;
  };
};

interface RelationshipExplorerProps {
  initialTermId?: number;
  width?: number;
  height?: number;
}

/**
 * RelationshipExplorer Component
 *
 * Interactive UI for exploring term relationships:
 * - Filters: Relationship types, confidence, depth
 * - Graph visualization with D3.js
 * - Node/edge selection and details
 * - Export graph data
 * - Extraction trigger for missing relationships
 */
export default function RelationshipExplorer({
  initialTermId,
  width = 1200,
  height = 800,
}: RelationshipExplorerProps) {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedTermIds] = useState<number[]>(initialTermId ? [initialTermId] : []);
  const [selectedRelationTypes, setSelectedRelationTypes] = useState<string[]>([]);
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [maxDepth, setMaxDepth] = useState(2);
  const [validatedOnly, setValidatedOnly] = useState(false);

  // Selected node/edge for details
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

  // Available relationship types
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);

  // Load graph data
  useEffect(() => {
    loadGraphData();
  }, [selectedTermIds, selectedRelationTypes, minConfidence, maxDepth, validatedOnly]);

  const loadGraphData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params: any = {
        min_confidence: minConfidence,
        max_depth: maxDepth,
        validated_only: validatedOnly,
      };

      if (selectedTermIds.length > 0) {
        params.term_ids = selectedTermIds;
      }

      if (selectedRelationTypes.length > 0) {
        params.relation_types = selectedRelationTypes;
      }

      // Fetch graph data
      const response = await apiClient.client.get('/api/relationships/graph/data', { params });
      setGraphData(response.data);

      // Update available types
      if (response.data.stats.relationship_types) {
        setAvailableTypes(response.data.stats.relationship_types);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  };

  const handleEdgeClick = (edge: GraphEdge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  };

  const handleExtractRelationships = async (termId: number) => {
    try {
      const response = await apiClient.client.post(`/api/relationships/extract/${termId}`, null, {
        params: { min_confidence: minConfidence },
      });

      alert(`Extracted ${response.data.created} new relationships for "${response.data.term}"`);
      loadGraphData(); // Reload to show new relationships
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Extraction failed');
    }
  };

  const handleExportGraph = () => {
    if (!graphData) return;

    const dataStr = JSON.stringify(graphData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `graph-data-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleRelationType = (type: string) => {
    setSelectedRelationTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  return (
    <div className="relationship-explorer">
      {/* Control Panel */}
      <div className="explorer-controls">
        <div className="controls-header">
          <h3 className="controls-title">Relationship Explorer</h3>
          <button className="export-button" onClick={handleExportGraph} disabled={!graphData}>
            📥 Export
          </button>
        </div>

        {/* Filters */}
        <div className="controls-section">
          <h4 className="section-title">Filters</h4>

          {/* Confidence Slider */}
          <div className="control-group">
            <label className="control-label">
              Min Confidence: {(minConfidence * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="confidence-slider"
            />
          </div>

          {/* Depth Selector */}
          <div className="control-group">
            <label className="control-label">Max Depth: {maxDepth}</label>
            <select
              value={maxDepth}
              onChange={(e) => setMaxDepth(parseInt(e.target.value))}
              className="depth-select"
            >
              <option value="1">1 hop</option>
              <option value="2">2 hops</option>
              <option value="3">3 hops</option>
              <option value="4">4 hops</option>
              <option value="5">5 hops</option>
            </select>
          </div>

          {/* Validated Only Checkbox */}
          <div className="control-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={validatedOnly}
                onChange={(e) => setValidatedOnly(e.target.checked)}
              />
              <span>Validated only</span>
            </label>
          </div>
        </div>

        {/* Relationship Types Filter */}
        {availableTypes.length > 0 && (
          <div className="controls-section">
            <h4 className="section-title">Relationship Types</h4>
            <div className="type-filters">
              {availableTypes.map(type => (
                <label key={type} className="type-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedRelationTypes.includes(type)}
                    onChange={() => toggleRelationType(type)}
                  />
                  <span className="type-label">{type.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Selected Node Details */}
        {selectedNode && (
          <div className="controls-section">
            <h4 className="section-title">Selected Term</h4>
            <div className="details-card">
              <div className="details-row">
                <strong>Term:</strong>
                <span>{selectedNode.label}</span>
              </div>
              <div className="details-row">
                <strong>Language:</strong>
                <span>{selectedNode.language.toUpperCase()}</span>
              </div>
              <div className="details-row">
                <strong>Definitions:</strong>
                <span>{selectedNode.definition_count}</span>
              </div>
              {selectedNode.group && (
                <div className="details-row">
                  <strong>Domain:</strong>
                  <span>{selectedNode.group}</span>
                </div>
              )}
              <button
                className="extract-button"
                onClick={() => handleExtractRelationships(selectedNode.id)}
              >
                🔍 Extract Relationships
              </button>
            </div>
          </div>
        )}

        {/* Selected Edge Details */}
        {selectedEdge && (
          <div className="controls-section">
            <h4 className="section-title">Selected Relationship</h4>
            <div className="details-card">
              <div className="details-row">
                <strong>Type:</strong>
                <span>{selectedEdge.type.replace('_', ' ')}</span>
              </div>
              <div className="details-row">
                <strong>Confidence:</strong>
                <span>{(selectedEdge.weight * 100).toFixed(0)}%</span>
              </div>
              <div className="details-row">
                <strong>Source:</strong>
                <span>Term ID {typeof selectedEdge.source === 'number' ? selectedEdge.source : (selectedEdge.source as any).id}</span>
              </div>
              <div className="details-row">
                <strong>Target:</strong>
                <span>Term ID {typeof selectedEdge.target === 'number' ? selectedEdge.target : (selectedEdge.target as any).id}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Graph Display */}
      <div className="graph-container">
        {loading ? (
          <div className="graph-loading">
            <div className="loading-spinner"></div>
            <p>Loading relationship graph...</p>
          </div>
        ) : error ? (
          <div className="graph-error">
            <div className="error-icon">⚠️</div>
            <h3>Error Loading Graph</h3>
            <p>{error}</p>
            <button className="retry-button" onClick={loadGraphData}>
              Retry
            </button>
          </div>
        ) : graphData && graphData.nodes.length > 0 ? (
          <GraphVisualization
            data={graphData}
            width={width}
            height={height}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
            highlightedNodeId={selectedNode?.id || null}
            selectedRelationTypes={selectedRelationTypes}
          />
        ) : (
          <div className="graph-empty">
            <div className="empty-icon">🔗</div>
            <h3>No Relationships Found</h3>
            <p>No relationships match your current filters.</p>
            <button className="reset-button" onClick={() => {
              setSelectedRelationTypes([]);
              setMinConfidence(0.5);
              setValidatedOnly(false);
            }}>
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
