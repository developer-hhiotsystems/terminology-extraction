import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import apiClient from '../api/client'

interface RelatedTerm {
  term_id: number
  term_text: string
  language: string
  definitions: string[]
  relationship_path: string[]
  distance: number
}

interface TermRelationshipsProps {
  termId: number
  termText: string
}

export default function TermRelationships({ termId, termText }: TermRelationshipsProps) {
  const [loading, setLoading] = useState(false)
  const [relatedTerms, setRelatedTerms] = useState<RelatedTerm[]>([])
  const [synonyms, setSynonyms] = useState<RelatedTerm[]>([])
  const [hierarchy, setHierarchy] = useState<{ parents: any[], children: any[] }>({ parents: [], children: [] })
  const [graphAvailable, setGraphAvailable] = useState(false)
  const [activeTab, setActiveTab] = useState<'related' | 'synonyms' | 'hierarchy'>('related')

  useEffect(() => {
    checkGraphStatus()
  }, [])

  useEffect(() => {
    if (graphAvailable) {
      loadRelationships()
    }
  }, [termId, graphAvailable])

  const checkGraphStatus = async () => {
    try {
      const response = await apiClient.client.get('/api/graph/status')
      setGraphAvailable(response.data.connected)
    } catch (error) {
      setGraphAvailable(false)
    }
  }

  const loadRelationships = async () => {
    setLoading(true)
    try {
      // Load all relationship types in parallel
      const [relatedResp, synonymsResp, hierarchyResp] = await Promise.all([
        apiClient.client.get(`/api/graph/terms/${termId}/related`, {
          params: { max_depth: 2 }
        }),
        apiClient.client.get(`/api/graph/terms/${termId}/synonyms`),
        apiClient.client.get(`/api/graph/terms/${termId}/hierarchy`)
      ])

      setRelatedTerms(relatedResp.data.related_terms || [])
      setSynonyms(synonymsResp.data.synonyms || [])
      setHierarchy(hierarchyResp.data || { parents: [], children: [] })
    } catch (error: any) {
      console.error('Failed to load relationships:', error)
      if (error.response?.status !== 503) {
        toast.error('Failed to load term relationships')
      }
    } finally {
      setLoading(false)
    }
  }

  if (!graphAvailable) {
    return (
      <div className="term-relationships-unavailable">
        <h3>📊 Term Relationships</h3>
        <p className="info-message">
          Knowledge graph features are not available.
          Start the Neo4j container to enable relationship discovery.
        </p>
        <pre className="code-block">docker-compose -f docker-compose.dev.yml up neo4j</pre>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="term-relationships">
        <h3>📊 Term Relationships</h3>
        <p className="loading-message">Loading relationships...</p>
      </div>
    )
  }

  const hasRelationships = relatedTerms.length > 0 || synonyms.length > 0 ||
                          hierarchy.parents.length > 0 || hierarchy.children.length > 0

  return (
    <div className="term-relationships">
      <h3>📊 Term Relationships for "{termText}"</h3>

      {!hasRelationships && (
        <p className="info-message">
          No relationships found. Terms must be synced to the knowledge graph first.
        </p>
      )}

      {hasRelationships && (
        <>
          {/* Tabs */}
          <div className="relationship-tabs">
            <button
              className={`tab-button ${activeTab === 'related' ? 'active' : ''}`}
              onClick={() => setActiveTab('related')}
            >
              Related ({relatedTerms.length})
            </button>
            <button
              className={`tab-button ${activeTab === 'synonyms' ? 'active' : ''}`}
              onClick={() => setActiveTab('synonyms')}
            >
              Synonyms ({synonyms.length})
            </button>
            <button
              className={`tab-button ${activeTab === 'hierarchy' ? 'active' : ''}`}
              onClick={() => setActiveTab('hierarchy')}
            >
              Hierarchy ({hierarchy.parents.length + hierarchy.children.length})
            </button>
          </div>

          {/* Content */}
          <div className="relationship-content">
            {activeTab === 'related' && (
              <div className="related-terms-list">
                {relatedTerms.length === 0 ? (
                  <p className="empty-message">No related terms found</p>
                ) : (
                  relatedTerms.map((term, index) => (
                    <div key={index} className="relationship-item">
                      <div className="term-info">
                        <span className="term-text">{term.term_text}</span>
                        <span className="term-lang">({term.language})</span>
                      </div>
                      <div className="relationship-meta">
                        <span className="distance">Distance: {term.distance}</span>
                        <span className="path">{term.relationship_path.join(' → ')}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'synonyms' && (
              <div className="synonyms-list">
                {synonyms.length === 0 ? (
                  <p className="empty-message">No synonyms found</p>
                ) : (
                  synonyms.map((term, index) => (
                    <div key={index} className="relationship-item synonym">
                      <div className="term-info">
                        <span className="term-text">{term.term_text}</span>
                        <span className="term-lang">({term.language})</span>
                      </div>
                      {term.definitions && term.definitions.length > 0 && (
                        <div className="term-definition">
                          {term.definitions[0].substring(0, 150)}
                          {term.definitions[0].length > 150 && '...'}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'hierarchy' && (
              <div className="hierarchy-view">
                {hierarchy.parents.length > 0 && (
                  <div className="hierarchy-section">
                    <h4>⬆️ Parent Terms</h4>
                    {hierarchy.parents.map((term, index) => (
                      <div key={index} className="relationship-item parent">
                        <span className="term-text">{term.term_text}</span>
                        <span className="term-lang">({term.language})</span>
                      </div>
                    ))}
                  </div>
                )}

                {hierarchy.children.length > 0 && (
                  <div className="hierarchy-section">
                    <h4>⬇️ Child Terms</h4>
                    {hierarchy.children.map((term, index) => (
                      <div key={index} className="relationship-item child">
                        <span className="term-text">{term.term_text}</span>
                        <span className="term-lang">({term.language})</span>
                      </div>
                    ))}
                  </div>
                )}

                {hierarchy.parents.length === 0 && hierarchy.children.length === 0 && (
                  <p className="empty-message">No hierarchical relationships found</p>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
