import { useState } from 'react';
import type { SearchResult } from '../types/search';
import './SearchResults.css';

interface SearchResultsProps {
  results: SearchResult[];
  totalResults: number;
  loading: boolean;
  error: string | null;
  query: string;
  currentPage?: number;
  resultsPerPage?: number;
  onPageChange?: (page: number) => void;
  onResultClick?: (result: SearchResult) => void;
}

export default function SearchResults({
  results,
  totalResults,
  loading,
  error,
  query,
  currentPage = 1,
  resultsPerPage = 20,
  onPageChange,
  onResultClick,
}: SearchResultsProps) {
  const totalPages = Math.ceil(totalResults / resultsPerPage);
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const toggleExpanded = (id: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const highlightSnippet = (snippet: string | null, searchQuery: string) => {
    if (!snippet) return null;
    if (!searchQuery.trim()) return snippet;

    // Remove quotes from phrase searches
    const cleanQuery = searchQuery.replace(/^"|"$/g, '');

    // Split by words and create regex (case-insensitive)
    const words = cleanQuery.split(/\s+/).filter(w => w.length > 0);
    const regex = new RegExp(`(${words.join('|')})`, 'gi');

    const parts = snippet.split(regex);
    return parts.map((part, i) =>
      regex.test(part) ? <mark key={i}>{part}</mark> : part
    );
  };

  const formatRelevanceScore = (score: number) => {
    return (score * 100).toFixed(1);
  };

  const getLanguageLabel = (lang: string) => {
    const labels: Record<string, string> = {
      en: 'English',
      de: 'German',
      fr: 'French',
      es: 'Spanish',
    };
    return labels[lang] || lang.toUpperCase();
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pageNumbers: (number | string)[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // Show abbreviated pagination
      pageNumbers.push(1);

      if (currentPage > 3) {
        pageNumbers.push('...');
      }

      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        pageNumbers.push(i);
      }

      if (currentPage < totalPages - 2) {
        pageNumbers.push('...');
      }

      pageNumbers.push(totalPages);
    }

    return (
      <div className="pagination">
        <button
          className="pagination-button"
          onClick={() => onPageChange?.(currentPage - 1)}
          disabled={currentPage === 1}
          title="Previous page"
        >
          ‹
        </button>

        {pageNumbers.map((page, index) => (
          typeof page === 'number' ? (
            <button
              key={index}
              className={`pagination-button ${page === currentPage ? 'active' : ''}`}
              onClick={() => onPageChange?.(page)}
            >
              {page}
            </button>
          ) : (
            <span key={index} className="pagination-ellipsis">
              {page}
            </span>
          )
        ))}

        <button
          className="pagination-button"
          onClick={() => onPageChange?.(currentPage + 1)}
          disabled={currentPage === totalPages}
          title="Next page"
        >
          ›
        </button>
      </div>
    );
  };

  // Loading state
  if (loading) {
    return (
      <div className="search-results-container">
        <div className="search-results-loading">
          <div className="loading-spinner"></div>
          <p>Searching glossary...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="search-results-container">
        <div className="search-results-error">
          <div className="error-icon">⚠️</div>
          <h3>Search Error</h3>
          <p>{error}</p>
          <small>Please try again or modify your search query.</small>
        </div>
      </div>
    );
  }

  // Empty state
  if (!query.trim()) {
    return (
      <div className="search-results-container">
        <div className="search-results-empty">
          <div className="empty-icon">🔍</div>
          <h3>Start Searching</h3>
          <p>Enter a search term to find glossary entries</p>
          <small>Try searching for technical terms, definitions, or concepts</small>
        </div>
      </div>
    );
  }

  // No results state
  if (results.length === 0) {
    return (
      <div className="search-results-container">
        <div className="search-results-empty">
          <div className="empty-icon">📭</div>
          <h3>No Results Found</h3>
          <p>No glossary entries match "{query}"</p>
          <div className="search-tips">
            <small><strong>Search Tips:</strong></small>
            <ul>
              <li>Try different keywords or synonyms</li>
              <li>Check your spelling</li>
              <li>Use wildcards for partial matches (e.g., temp*)</li>
              <li>Try Boolean operators (AND, OR, NOT)</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  // Results display
  return (
    <div className="search-results-container">
      {/* Results Header */}
      <div className="search-results-header">
        <div className="results-count">
          <strong>{totalResults.toLocaleString()}</strong> result{totalResults !== 1 ? 's' : ''} for "{query}"
        </div>
        <div className="results-info">
          Page {currentPage} of {totalPages} • Showing {results.length} entries
        </div>
      </div>

      {/* Results List */}
      <div className="search-results-list">
        {results.map((result) => {
          const isExpanded = expandedIds.has(result.id);
          const hasMultipleDefinitions = result.definitions.length > 1;

          return (
            <div
              key={result.id}
              className="result-card"
              onClick={() => onResultClick?.(result)}
            >
              {/* Result Header */}
              <div className="result-header">
                <div className="result-term-section">
                  <h3 className="result-term">{result.term}</h3>
                  <div className="result-meta">
                    <span className="result-language" title={`Language: ${getLanguageLabel(result.language)}`}>
                      {getLanguageLabel(result.language)}
                    </span>
                    {result.domain_tags.length > 0 && (
                      <span className="result-domain" title="Domain">
                        {result.domain_tags[0]}
                      </span>
                    )}
                  </div>
                </div>

                <div className="result-score" title={`Relevance Score: ${formatRelevanceScore(result.relevance_score)}%`}>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${formatRelevanceScore(result.relevance_score)}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{formatRelevanceScore(result.relevance_score)}%</span>
                </div>
              </div>

              {/* Snippet */}
              {result.snippet && (
                <div className="result-snippet">
                  {highlightSnippet(result.snippet, query)}
                </div>
              )}

              {/* Definitions */}
              <div className="result-definitions">
                {result.definitions.slice(0, isExpanded ? undefined : 1).map((def: any, index: number) => (
                  <div key={index} className="definition-item">
                    <span className="definition-text">{def.definition_text || def}</span>
                  </div>
                ))}

                {hasMultipleDefinitions && (
                  <button
                    className="expand-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExpanded(result.id);
                    }}
                  >
                    {isExpanded
                      ? `▲ Show less (${result.definitions.length - 1} hidden)`
                      : `▼ Show ${result.definitions.length - 1} more definition${result.definitions.length - 1 !== 1 ? 's' : ''}`
                    }
                  </button>
                )}
              </div>

              {/* Source */}
              <div className="result-footer">
                <small className="result-source" title={`Source: ${result.source}`}>
                  📄 {result.source}
                </small>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {renderPagination()}
    </div>
  );
}
