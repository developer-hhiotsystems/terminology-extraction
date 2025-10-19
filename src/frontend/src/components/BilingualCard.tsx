import { useState, useRef } from 'react';
import type { GlossaryEntry } from '../types';
import './BilingualCard.css';

interface BilingualCardProps {
  entry: GlossaryEntry;
  onEdit?: (entry: GlossaryEntry) => void;
  onDelete?: (id: number) => void;
  onSelect?: (id: number, selected: boolean) => void;
  selected?: boolean;
  showCheckbox?: boolean;
  compact?: boolean;
}

/**
 * BilingualCard Component
 *
 * Displays glossary entries in a side-by-side bilingual view with:
 * - Synchronized scrolling between language versions
 * - Language toggle for mobile
 * - Visual language indicators
 * - Edit and delete actions
 * - Selection checkbox for bulk operations
 * - Compact mode for lists
 *
 * Perfect for bilingual glossaries where users need to compare
 * English and German terms side-by-side.
 */
export default function BilingualCard({
  entry,
  onEdit,
  onDelete,
  onSelect,
  selected = false,
  showCheckbox = false,
  compact = false,
}: BilingualCardProps) {
  const [activeLanguage, setActiveLanguage] = useState<'en' | 'de' | 'both'>('both');
  const [syncScroll, setSyncScroll] = useState(true);
  const enScrollRef = useRef<HTMLDivElement>(null);
  const deScrollRef = useRef<HTMLDivElement>(null);
  const isScrolling = useRef(false);

  // Get definitions by language
  const enDefinitions = entry.definitions?.filter(d => d.language === 'en') || [];
  const deDefinitions = entry.definitions?.filter(d => d.language === 'de') || [];

  // Synchronized scrolling
  const handleScroll = (source: 'en' | 'de') => {
    if (!syncScroll || isScrolling.current) return;

    isScrolling.current = true;
    const sourceRef = source === 'en' ? enScrollRef : deScrollRef;
    const targetRef = source === 'en' ? deScrollRef : enScrollRef;

    if (sourceRef.current && targetRef.current) {
      const scrollPercentage =
        sourceRef.current.scrollTop /
        (sourceRef.current.scrollHeight - sourceRef.current.clientHeight || 1);

      targetRef.current.scrollTop =
        scrollPercentage * (targetRef.current.scrollHeight - targetRef.current.clientHeight);
    }

    setTimeout(() => {
      isScrolling.current = false;
    }, 100);
  };

  // Format page numbers
  const formatPageNumbers = (pageNumbers?: number[]) => {
    if (!pageNumbers || pageNumbers.length === 0) return 'N/A';
    return pageNumbers.sort((a, b) => a - b).join(', ');
  };

  // Get validation status badge
  const getValidationBadge = () => {
    const status = entry.validation_status || 'pending';
    const badges: Record<string, { label: string; className: string }> = {
      validated: { label: '✓ Validated', className: 'badge-validated' },
      pending: { label: '⏳ Pending', className: 'badge-pending' },
      rejected: { label: '✗ Rejected', className: 'badge-rejected' },
    };
    return badges[status] || badges.pending;
  };

  const validationBadge = getValidationBadge();

  return (
    <div className={`bilingual-card ${compact ? 'compact' : ''} ${selected ? 'selected' : ''}`}>
      {/* Card Header */}
      <div className="bilingual-card-header">
        <div className="header-left">
          {showCheckbox && (
            <input
              type="checkbox"
              className="card-checkbox"
              checked={selected}
              onChange={(e) => onSelect?.(entry.id, e.target.checked)}
              title="Select for bulk operations"
            />
          )}
          <h3 className="card-term">{entry.term}</h3>
        </div>

        <div className="header-right">
          {/* Validation Status */}
          <span className={`validation-badge ${validationBadge.className}`}>
            {validationBadge.label}
          </span>

          {/* Language Toggle (Mobile) */}
          <div className="language-toggle mobile-only">
            <button
              className={`lang-btn ${activeLanguage === 'en' ? 'active' : ''}`}
              onClick={() => setActiveLanguage('en')}
            >
              EN
            </button>
            <button
              className={`lang-btn ${activeLanguage === 'de' ? 'active' : ''}`}
              onClick={() => setActiveLanguage('de')}
            >
              DE
            </button>
            <button
              className={`lang-btn ${activeLanguage === 'both' ? 'active' : ''}`}
              onClick={() => setActiveLanguage('both')}
            >
              Both
            </button>
          </div>

          {/* Sync Scroll Toggle (Desktop) */}
          <button
            className={`sync-toggle desktop-only ${syncScroll ? 'active' : ''}`}
            onClick={() => setSyncScroll(!syncScroll)}
            title={syncScroll ? 'Disable synchronized scrolling' : 'Enable synchronized scrolling'}
          >
            {syncScroll ? '🔗' : '🔓'}
          </button>

          {/* Actions */}
          <div className="card-actions">
            {onEdit && (
              <button
                className="action-btn edit-btn"
                onClick={() => onEdit(entry)}
                title="Edit entry"
              >
                ✏️
              </button>
            )}
            {onDelete && (
              <button
                className="action-btn delete-btn"
                onClick={() => onDelete(entry.id)}
                title="Delete entry"
              >
                🗑️
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Bilingual Content */}
      <div className="bilingual-content">
        {/* English Section */}
        {(activeLanguage === 'both' || activeLanguage === 'en') && (
          <div className={`language-section ${activeLanguage === 'both' ? 'split' : 'full'}`}>
            <div className="section-header">
              <span className="language-flag">🇬🇧</span>
              <h4 className="section-title">English</h4>
              {enDefinitions.length > 0 && (
                <span className="definition-count">{enDefinitions.length} definition{enDefinitions.length !== 1 ? 's' : ''}</span>
              )}
            </div>

            <div
              ref={enScrollRef}
              className="definitions-container"
              onScroll={() => handleScroll('en')}
            >
              {enDefinitions.length > 0 ? (
                enDefinitions.map((def, index) => (
                  <div key={index} className="definition-item">
                    <div className="definition-text">{def.definition_text}</div>
                    {def.context && (
                      <div className="definition-context">
                        <small>Context: {def.context}</small>
                      </div>
                    )}
                    {def.page_number && (
                      <div className="definition-page">
                        <small>Page {def.page_number}</small>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-definitions">
                  <small>No English definitions available</small>
                </div>
              )}
            </div>
          </div>
        )}

        {/* German Section */}
        {(activeLanguage === 'both' || activeLanguage === 'de') && (
          <div className={`language-section ${activeLanguage === 'both' ? 'split' : 'full'}`}>
            <div className="section-header">
              <span className="language-flag">🇩🇪</span>
              <h4 className="section-title">German (Deutsch)</h4>
              {deDefinitions.length > 0 && (
                <span className="definition-count">{deDefinitions.length} definition{deDefinitions.length !== 1 ? 's' : ''}</span>
              )}
            </div>

            <div
              ref={deScrollRef}
              className="definitions-container"
              onScroll={() => handleScroll('de')}
            >
              {deDefinitions.length > 0 ? (
                deDefinitions.map((def, index) => (
                  <div key={index} className="definition-item">
                    <div className="definition-text">{def.definition_text}</div>
                    {def.context && (
                      <div className="definition-context">
                        <small>Kontext: {def.context}</small>
                      </div>
                    )}
                    {def.page_number && (
                      <div className="definition-page">
                        <small>Seite {def.page_number}</small>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-definitions">
                  <small>Keine deutschen Definitionen verfügbar</small>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Card Footer */}
      {!compact && (
        <div className="bilingual-card-footer">
          <div className="footer-meta">
            <small className="meta-item">
              <strong>Source:</strong> {entry.source_document || 'Unknown'}
            </small>
            <small className="meta-item">
              <strong>Pages:</strong> {formatPageNumbers(entry.page_numbers)}
            </small>
            {entry.domain_tags && entry.domain_tags.length > 0 && (
              <small className="meta-item">
                <strong>Domain:</strong> {entry.domain_tags.join(', ')}
              </small>
            )}
            {entry.confidence_score !== undefined && (
              <small className="meta-item">
                <strong>Confidence:</strong> {(entry.confidence_score * 100).toFixed(0)}%
              </small>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
