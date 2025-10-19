import { useState, useEffect } from 'react';
import type { SearchMode, SearchFilters } from '../types/search';
import './AdvancedSearch.css';

interface AdvancedSearchProps {
  mode: SearchMode;
  filters: SearchFilters;
  onModeChange: (mode: SearchMode) => void;
  onFiltersChange: (filters: Partial<SearchFilters>) => void;
  onClearFilters: () => void;
  onInsertOperator?: (operator: string) => void;
  availableLanguages?: string[];
  availableDomains?: string[];
}

export default function AdvancedSearch({
  mode,
  filters,
  onModeChange,
  onFiltersChange,
  onClearFilters,
  onInsertOperator,
  availableLanguages = ['en', 'de'],
  availableDomains = [],
}: AdvancedSearchProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeFiltersCount, setActiveFiltersCount] = useState(0);

  // Count active filters
  useEffect(() => {
    let count = 0;
    if (filters.language) count++;
    if (filters.domain) count++;
    if (mode !== 'simple') count++;
    setActiveFiltersCount(count);
  }, [filters, mode]);

  const getLanguageLabel = (lang: string) => {
    const labels: Record<string, string> = {
      en: 'English',
      de: 'German',
      fr: 'French',
      es: 'Spanish',
    };
    return labels[lang] || lang.toUpperCase();
  };

  const getModeDescription = (m: SearchMode) => {
    switch (m) {
      case 'phrase':
        return 'Search for exact phrase matches';
      case 'boolean':
        return 'Use AND, OR, NOT operators for complex queries';
      case 'wildcard':
        return 'Use * for prefix matching (e.g., temp*)';
      case 'simple':
      default:
        return 'Basic keyword search with stemming';
    }
  };

  const handleLanguageChange = (lang: string) => {
    onFiltersChange({ language: lang || undefined });
  };

  const handleDomainChange = (domain: string) => {
    onFiltersChange({ domain: domain || undefined });
  };

  const insertBooleanOperator = (operator: string) => {
    if (onInsertOperator) {
      onInsertOperator(` ${operator} `);
    }
  };

  return (
    <div className="advanced-search-container">
      {/* Toggle Button */}
      <button
        className="advanced-search-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        title={isExpanded ? 'Hide advanced options' : 'Show advanced options'}
      >
        <span className="toggle-icon">{isExpanded ? '▲' : '▼'}</span>
        <span className="toggle-text">Advanced Search</span>
        {activeFiltersCount > 0 && (
          <span className="filter-badge">{activeFiltersCount}</span>
        )}
      </button>

      {/* Advanced Options Panel */}
      {isExpanded && (
        <div className="advanced-search-panel">
          {/* Search Modes */}
          <div className="search-section">
            <h4 className="section-title">Search Mode</h4>
            <div className="mode-options">
              {(['simple', 'phrase', 'boolean', 'wildcard'] as SearchMode[]).map((m) => (
                <label key={m} className={`mode-option ${mode === m ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="search-mode"
                    value={m}
                    checked={mode === m}
                    onChange={() => onModeChange(m)}
                  />
                  <span className="mode-label">{m.charAt(0).toUpperCase() + m.slice(1)}</span>
                  <span className="mode-description">{getModeDescription(m)}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Boolean Operators (only shown in Boolean mode) */}
          {mode === 'boolean' && onInsertOperator && (
            <div className="search-section">
              <h4 className="section-title">Boolean Operators</h4>
              <div className="operator-buttons">
                <button
                  className="operator-button"
                  onClick={() => insertBooleanOperator('AND')}
                  title="Both terms must be present"
                >
                  AND
                </button>
                <button
                  className="operator-button"
                  onClick={() => insertBooleanOperator('OR')}
                  title="Either term can be present"
                >
                  OR
                </button>
                <button
                  className="operator-button"
                  onClick={() => insertBooleanOperator('NOT')}
                  title="Exclude this term"
                >
                  NOT
                </button>
                <button
                  className="operator-button"
                  onClick={() => insertBooleanOperator('(')}
                  title="Group terms with parentheses"
                >
                  ( )
                </button>
              </div>
              <div className="operator-examples">
                <small>
                  <strong>Examples:</strong>
                  <br />
                  • temperature AND control
                  <br />
                  • sensor OR actuator
                  <br />
                  • heating NOT cooling
                  <br />• (thermal OR heat) AND management
                </small>
              </div>
            </div>
          )}

          {/* Filters */}
          <div className="search-section">
            <h4 className="section-title">Filters</h4>

            <div className="filter-grid">
              {/* Language Filter */}
              <div className="filter-group">
                <label htmlFor="language-filter" className="filter-label">
                  Language
                </label>
                <select
                  id="language-filter"
                  className="filter-select"
                  value={filters.language || ''}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                >
                  <option value="">All Languages</option>
                  {availableLanguages.map((lang) => (
                    <option key={lang} value={lang}>
                      {getLanguageLabel(lang)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Domain Filter */}
              {availableDomains.length > 0 && (
                <div className="filter-group">
                  <label htmlFor="domain-filter" className="filter-label">
                    Domain
                  </label>
                  <select
                    id="domain-filter"
                    className="filter-select"
                    value={filters.domain || ''}
                    onChange={(e) => handleDomainChange(e.target.value)}
                  >
                    <option value="">All Domains</option>
                    {availableDomains.map((domain) => (
                      <option key={domain} value={domain}>
                        {domain}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Results Per Page */}
              <div className="filter-group">
                <label htmlFor="limit-filter" className="filter-label">
                  Results Per Page
                </label>
                <select
                  id="limit-filter"
                  className="filter-select"
                  value={filters.limit || 20}
                  onChange={(e) => onFiltersChange({ limit: parseInt(e.target.value) })}
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>
          </div>

          {/* Active Filters Display */}
          {activeFiltersCount > 0 && (
            <div className="active-filters">
              <div className="active-filters-header">
                <span className="active-filters-title">Active Filters ({activeFiltersCount}):</span>
                <button className="clear-filters-button" onClick={onClearFilters}>
                  Clear All
                </button>
              </div>
              <div className="active-filters-list">
                {mode !== 'simple' && (
                  <span className="filter-tag">
                    Mode: {mode}
                    <button
                      className="remove-filter"
                      onClick={() => onModeChange('simple')}
                      title="Remove mode filter"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.language && (
                  <span className="filter-tag">
                    Language: {getLanguageLabel(filters.language)}
                    <button
                      className="remove-filter"
                      onClick={() => handleLanguageChange('')}
                      title="Remove language filter"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.domain && (
                  <span className="filter-tag">
                    Domain: {filters.domain}
                    <button
                      className="remove-filter"
                      onClick={() => handleDomainChange('')}
                      title="Remove domain filter"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Search Tips */}
          <div className="search-tips-section">
            <h4 className="section-title">Search Tips</h4>
            <div className="tips-grid">
              <div className="tip-card">
                <strong>Simple Mode</strong>
                <p>Searches all terms with automatic stemming. Most common use case.</p>
              </div>
              <div className="tip-card">
                <strong>Phrase Mode</strong>
                <p>Finds exact phrase matches. Use for specific terminology.</p>
              </div>
              <div className="tip-card">
                <strong>Boolean Mode</strong>
                <p>Combine terms with AND, OR, NOT. Great for complex queries.</p>
              </div>
              <div className="tip-card">
                <strong>Wildcard Mode</strong>
                <p>Use * for prefix matching. Example: temp* finds temperature, temporal, etc.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
