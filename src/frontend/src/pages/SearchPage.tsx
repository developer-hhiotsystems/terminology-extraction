import { useRef } from 'react';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import AdvancedSearch from '../components/AdvancedSearch';
import { useSearch } from '../hooks/useSearch';
import type { SearchResult } from '../types/search';
import './SearchPage.css';

/**
 * SearchPage - Complete FTS5 Search Integration Example
 *
 * This page demonstrates how to integrate all the FTS5 search components:
 * - SearchBar: Main search input with autocomplete
 * - AdvancedSearch: Filters and Boolean operators
 * - SearchResults: Results display with pagination
 * - useSearch: Custom hook managing all search state
 *
 * Features:
 * - Real-time autocomplete suggestions
 * - Multiple search modes (Simple, Phrase, Boolean, Wildcard)
 * - Language and domain filtering
 * - URL state synchronization (shareable searches)
 * - Keyboard navigation
 * - Pagination
 * - BM25 relevance scoring
 */
export default function SearchPage() {
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Use the search hook - handles all state management
  const {
    query,
    mode,
    filters,
    results,
    totalResults,
    loading,
    error,
    suggestions,
    showSuggestions,
    setQuery,
    setMode,
    setFilters,
    search,
    selectSuggestion,
    clearSearch,
    hideSuggestions,
  } = useSearch({
    initialQuery: '',
    initialMode: 'simple',
    debounceMs: 300,
  });

  // Handle result click - navigate to term detail
  const handleResultClick = (result: SearchResult) => {
    console.log('Result clicked:', result);
    // TODO: Navigate to term detail page
    // Example: navigate(`/glossary/${result.id}`);
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    const newOffset = (page - 1) * (filters.limit || 20);
    setFilters({ offset: newOffset });
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Insert Boolean operator at cursor position
  const handleInsertOperator = (operator: string) => {
    if (searchInputRef.current) {
      const input = searchInputRef.current;
      const start = input.selectionStart || query.length;
      const end = input.selectionEnd || query.length;
      const newQuery = query.substring(0, start) + operator + query.substring(end);
      setQuery(newQuery);

      // Set cursor position after operator
      setTimeout(() => {
        input.focus();
        input.setSelectionRange(start + operator.length, start + operator.length);
      }, 0);
    } else {
      // Fallback: append to end
      setQuery(query + operator);
    }
  };

  // Clear all filters and reset to simple mode
  const handleClearFilters = () => {
    setMode('simple');
    setFilters({ language: undefined, domain: undefined, limit: 20, offset: 0 });
  };

  const currentPage = Math.floor((filters.offset || 0) / (filters.limit || 20)) + 1;

  return (
    <div className="search-page">
      {/* Page Header */}
      <div className="search-page-header">
        <h1 className="page-title">Glossary Search</h1>
        <p className="page-description">
          Powered by SQLite FTS5 Full-Text Search - 10.6x faster than traditional search
        </p>
      </div>

      {/* Main Search Bar */}
      <SearchBar
        query={query}
        mode={mode}
        loading={loading}
        suggestions={suggestions}
        showSuggestions={showSuggestions}
        onQueryChange={setQuery}
        onModeChange={setMode}
        onSearch={search}
        onSuggestionSelect={selectSuggestion}
        onHideSuggestions={hideSuggestions}
        onClear={clearSearch}
      />

      {/* Advanced Search Options */}
      <AdvancedSearch
        mode={mode}
        filters={filters}
        onModeChange={setMode}
        onFiltersChange={setFilters}
        onClearFilters={handleClearFilters}
        onInsertOperator={handleInsertOperator}
        availableLanguages={['en', 'de']}
        availableDomains={[]} // TODO: Populate from API
      />

      {/* Search Results */}
      <SearchResults
        results={results}
        totalResults={totalResults}
        loading={loading}
        error={error}
        query={query}
        currentPage={currentPage}
        resultsPerPage={filters.limit || 20}
        onPageChange={handlePageChange}
        onResultClick={handleResultClick}
      />

      {/* Search Stats Footer */}
      {results.length > 0 && (
        <div className="search-stats-footer">
          <small>
            🚀 FTS5 Search • BM25 Ranking • Porter Stemming • Phrase & Boolean Support
          </small>
        </div>
      )}
    </div>
  );
}
