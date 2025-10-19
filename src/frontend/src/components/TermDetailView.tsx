import { useState, useEffect } from 'react';
import type { GlossaryEntry } from '../types';
import apiClient from '../api/client';
import './TermDetailView.css';

interface TermDetailViewProps {
  entry: GlossaryEntry;
  onClose?: () => void;
  onEdit?: (entry: GlossaryEntry) => void;
  onDelete?: (id: number) => void;
  onRelatedTermClick?: (termId: number) => void;
}

/**
 * TermDetailView Component
 *
 * Enhanced term detail view with:
 * - Full bilingual definitions
 * - Related terms discovery
 * - Source document information
 * - Validation status and confidence
 * - Edit and delete actions
 * - Definition history (if available)
 * - Domain tags and metadata
 *
 * Use for dedicated term pages or modal views
 */
export default function TermDetailView({
  entry,
  onClose,
  onEdit,
  onDelete,
  onRelatedTermClick,
}: TermDetailViewProps) {
  const [relatedTerms, setRelatedTerms] = useState<GlossaryEntry[]>([]);
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [activeTab, setActiveTab] = useState<'definitions' | 'metadata' | 'related'>('definitions');

  // Load related terms on mount
  useEffect(() => {
    loadRelatedTerms();
  }, [entry.id]);

  const loadRelatedTerms = async () => {
    setLoadingRelated(true);
    try {
      // Search for related terms using the same source document
      const results = await apiClient.getGlossaryEntries({
        source: entry.source_document,
        limit: 10,
      });

      // Filter out current term and limit to 5 related
      const related = results
        .filter(r => r.id !== entry.id)
        .slice(0, 5);

      setRelatedTerms(related);
    } catch (error) {
      console.error('Failed to load related terms:', error);
    } finally {
      setLoadingRelated(false);
    }
  };

  // Get definitions by language
  const enDefinitions = entry.definitions?.filter(d => d.language === 'en') || [];
  const deDefinitions = entry.definitions?.filter(d => d.language === 'de') || [];

  // Format page numbers
  const formatPageNumbers = (pageNumbers?: number[]) => {
    if (!pageNumbers || pageNumbers.length === 0) return 'N/A';
    return pageNumbers.sort((a, b) => a - b).join(', ');
  };

  // Get validation badge
  const getValidationBadge = () => {
    const status = entry.validation_status || 'pending';
    const badges: Record<string, { label: string; icon: string; className: string }> = {
      validated: { label: 'Validated', icon: '✓', className: 'status-validated' },
      pending: { label: 'Pending Review', icon: '⏳', className: 'status-pending' },
      rejected: { label: 'Rejected', icon: '✗', className: 'status-rejected' },
    };
    return badges[status] || badges.pending;
  };

  const validationBadge = getValidationBadge();

  return (
    <div className="term-detail-view">
      {/* Header */}
      <div className="detail-header">
        <div className="header-content">
          <h1 className="detail-term">{entry.term}</h1>
          <div className="header-badges">
            <span className={`validation-status ${validationBadge.className}`}>
              <span className="status-icon">{validationBadge.icon}</span>
              <span className="status-label">{validationBadge.label}</span>
            </span>
            {entry.confidence_score !== undefined && (
              <span className="confidence-badge">
                Confidence: {(entry.confidence_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>

        <div className="header-actions">
          {onEdit && (
            <button
              className="action-button edit-button"
              onClick={() => onEdit(entry)}
              title="Edit term"
            >
              ✏️ Edit
            </button>
          )}
          {onDelete && (
            <button
              className="action-button delete-button"
              onClick={() => onDelete(entry.id)}
              title="Delete term"
            >
              🗑️ Delete
            </button>
          )}
          {onClose && (
            <button
              className="action-button close-button"
              onClick={onClose}
              title="Close"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="detail-tabs">
        <button
          className={`tab-button ${activeTab === 'definitions' ? 'active' : ''}`}
          onClick={() => setActiveTab('definitions')}
        >
          📖 Definitions
        </button>
        <button
          className={`tab-button ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
        >
          ℹ️ Metadata
        </button>
        <button
          className={`tab-button ${activeTab === 'related' ? 'active' : ''}`}
          onClick={() => setActiveTab('related')}
        >
          🔗 Related Terms {relatedTerms.length > 0 && `(${relatedTerms.length})`}
        </button>
      </div>

      {/* Tab Content */}
      <div className="detail-content">
        {/* Definitions Tab */}
        {activeTab === 'definitions' && (
          <div className="definitions-tab">
            {/* English Definitions */}
            <div className="language-section">
              <div className="language-header">
                <span className="language-flag">🇬🇧</span>
                <h2 className="language-title">English</h2>
                <span className="definition-count">
                  {enDefinitions.length} definition{enDefinitions.length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="definitions-list">
                {enDefinitions.length > 0 ? (
                  enDefinitions.map((def, index) => (
                    <div key={index} className="definition-card">
                      <div className="definition-number">Definition {index + 1}</div>
                      <p className="definition-text">{def.definition_text}</p>
                      {def.context && (
                        <div className="definition-context">
                          <strong>Context:</strong> {def.context}
                        </div>
                      )}
                      {def.page_number && (
                        <div className="definition-page">
                          <strong>Page:</strong> {def.page_number}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="no-definitions">
                    No English definitions available
                  </div>
                )}
              </div>
            </div>

            {/* German Definitions */}
            <div className="language-section">
              <div className="language-header">
                <span className="language-flag">🇩🇪</span>
                <h2 className="language-title">German (Deutsch)</h2>
                <span className="definition-count">
                  {deDefinitions.length} definition{deDefinitions.length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="definitions-list">
                {deDefinitions.length > 0 ? (
                  deDefinitions.map((def, index) => (
                    <div key={index} className="definition-card">
                      <div className="definition-number">Definition {index + 1}</div>
                      <p className="definition-text">{def.definition_text}</p>
                      {def.context && (
                        <div className="definition-context">
                          <strong>Kontext:</strong> {def.context}
                        </div>
                      )}
                      {def.page_number && (
                        <div className="definition-page">
                          <strong>Seite:</strong> {def.page_number}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="no-definitions">
                    Keine deutschen Definitionen verfügbar
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Metadata Tab */}
        {activeTab === 'metadata' && (
          <div className="metadata-tab">
            <div className="metadata-grid">
              <div className="metadata-card">
                <h3 className="metadata-title">Source Information</h3>
                <div className="metadata-items">
                  <div className="metadata-item">
                    <span className="metadata-label">Document:</span>
                    <span className="metadata-value">{entry.source_document || 'Unknown'}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Pages:</span>
                    <span className="metadata-value">{formatPageNumbers(entry.page_numbers)}</span>
                  </div>
                  {entry.document_type && (
                    <div className="metadata-item">
                      <span className="metadata-label">Document Type:</span>
                      <span className="metadata-value">{entry.document_type}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="metadata-card">
                <h3 className="metadata-title">Classification</h3>
                <div className="metadata-items">
                  <div className="metadata-item">
                    <span className="metadata-label">Language:</span>
                    <span className="metadata-value">{entry.language?.toUpperCase() || 'N/A'}</span>
                  </div>
                  {entry.domain_tags && entry.domain_tags.length > 0 && (
                    <div className="metadata-item">
                      <span className="metadata-label">Domains:</span>
                      <div className="domain-tags">
                        {entry.domain_tags.map((tag, index) => (
                          <span key={index} className="domain-tag">{tag}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="metadata-card">
                <h3 className="metadata-title">Quality Metrics</h3>
                <div className="metadata-items">
                  {entry.confidence_score !== undefined && (
                    <div className="metadata-item">
                      <span className="metadata-label">Confidence Score:</span>
                      <div className="confidence-bar-container">
                        <div
                          className="confidence-bar-fill"
                          style={{ width: `${entry.confidence_score * 100}%` }}
                        ></div>
                        <span className="confidence-percentage">
                          {(entry.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                  <div className="metadata-item">
                    <span className="metadata-label">Validation Status:</span>
                    <span className={`metadata-value ${validationBadge.className}`}>
                      {validationBadge.label}
                    </span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Total Definitions:</span>
                    <span className="metadata-value">{entry.definitions?.length || 0}</span>
                  </div>
                </div>
              </div>

              {entry.created_at && (
                <div className="metadata-card">
                  <h3 className="metadata-title">History</h3>
                  <div className="metadata-items">
                    <div className="metadata-item">
                      <span className="metadata-label">Created:</span>
                      <span className="metadata-value">
                        {new Date(entry.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {entry.updated_at && (
                      <div className="metadata-item">
                        <span className="metadata-label">Last Updated:</span>
                        <span className="metadata-value">
                          {new Date(entry.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Related Terms Tab */}
        {activeTab === 'related' && (
          <div className="related-tab">
            <h3 className="related-title">
              Terms from the same source: "{entry.source_document}"
            </h3>

            {loadingRelated ? (
              <div className="loading-related">
                <div className="spinner"></div>
                <p>Loading related terms...</p>
              </div>
            ) : relatedTerms.length > 0 ? (
              <div className="related-terms-list">
                {relatedTerms.map((relatedEntry) => (
                  <div
                    key={relatedEntry.id}
                    className="related-term-card"
                    onClick={() => onRelatedTermClick?.(relatedEntry.id)}
                  >
                    <h4 className="related-term-name">{relatedEntry.term}</h4>
                    <p className="related-term-preview">
                      {relatedEntry.definitions?.[0]?.definition_text?.slice(0, 150)}
                      {(relatedEntry.definitions?.[0]?.definition_text?.length || 0) > 150 ? '...' : ''}
                    </p>
                    <div className="related-term-meta">
                      <span className="related-term-pages">
                        Pages: {formatPageNumbers(relatedEntry.page_numbers)}
                      </span>
                      {relatedEntry.definitions && (
                        <span className="related-term-defs">
                          {relatedEntry.definitions.length} definition{relatedEntry.definitions.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-related-terms">
                <p>No related terms found in the same document.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
