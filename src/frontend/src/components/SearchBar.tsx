import { useRef, useEffect, KeyboardEvent } from 'react';
import type { SearchMode } from '../types/search';
import './SearchBar.css';

interface SearchBarProps {
  query: string;
  mode: SearchMode;
  loading: boolean;
  suggestions: string[];
  showSuggestions: boolean;
  onQueryChange: (query: string) => void;
  onModeChange: (mode: SearchMode) => void;
  onSearch: () => void;
  onSuggestionSelect: (suggestion: string) => void;
  onHideSuggestions: () => void;
  onClear: () => void;
}

export default function SearchBar({
  query,
  mode,
  loading,
  suggestions,
  showSuggestions,
  onQueryChange,
  onModeChange,
  onSearch,
  onSuggestionSelect,
  onHideSuggestions,
  onClear,
}: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const selectedIndexRef = useRef(-1);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Enter') {
        onSearch();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        selectedIndexRef.current = Math.min(
          selectedIndexRef.current + 1,
          suggestions.length - 1
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        selectedIndexRef.current = Math.max(selectedIndexRef.current - 1, -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndexRef.current >= 0) {
          onSuggestionSelect(suggestions[selectedIndexRef.current]);
        } else {
          onSearch();
        }
        selectedIndexRef.current = -1;
        break;
      case 'Escape':
        onHideSuggestions();
        selectedIndexRef.current = -1;
        break;
    }
  };

  const getModeIcon = (m: SearchMode) => {
    switch (m) {
      case 'phrase':
        return '"..."';
      case 'boolean':
        return 'AND/OR';
      case 'wildcard':
        return '*';
      case 'simple':
      default:
        return 'ABC';
    }
  };

  const getModeTooltip = (m: SearchMode) => {
    switch (m) {
      case 'phrase':
        return 'Phrase search - exact match';
      case 'boolean':
        return 'Boolean search - use AND/OR/NOT';
      case 'wildcard':
        return 'Wildcard search - prefix matching';
      case 'simple':
      default:
        return 'Simple search - basic keyword';
    }
  };

  return (
    <div className="search-bar-container">
      <div className="search-bar">
        {/* Search Mode Selector */}
        <div className="search-mode-selector">
          <select
            value={mode}
            onChange={(e) => onModeChange(e.target.value as SearchMode)}
            className="mode-select"
            title={getModeTooltip(mode)}
          >
            <option value="simple">Simple</option>
            <option value="phrase">Phrase</option>
            <option value="boolean">Boolean</option>
            <option value="wildcard">Wildcard</option>
          </select>
        </div>

        {/* Search Input */}
        <div className="search-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              mode === 'phrase'
                ? 'Search for exact phrase...'
                : mode === 'boolean'
                ? 'Use AND, OR, NOT operators...'
                : mode === 'wildcard'
                ? 'Search with * wildcard...'
                : 'Search glossary...'
            }
            className="search-input"
            disabled={loading}
          />

          {/* Loading Spinner */}
          {loading && (
            <div className="search-loading">
              <div className="spinner"></div>
            </div>
          )}

          {/* Clear Button */}
          {query && !loading && (
            <button
              type="button"
              onClick={onClear}
              className="clear-button"
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>

        {/* Search Button */}
        <button
          type="button"
          onClick={onSearch}
          className="search-button"
          disabled={!query.trim() || loading}
          title="Search (Enter)"
        >
          🔍 Search
        </button>
      </div>

      {/* Autocomplete Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div ref={suggestionsRef} className="suggestions-dropdown">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className={`suggestion-item ${
                index === selectedIndexRef.current ? 'selected' : ''
              }`}
              onClick={() => onSuggestionSelect(suggestion)}
              onMouseEnter={() => {
                selectedIndexRef.current = index;
              }}
            >
              <span className="suggestion-icon">🔍</span>
              <span className="suggestion-text">{suggestion}</span>
            </div>
          ))}
          <div className="suggestions-footer">
            <small>
              ↑↓ Navigate • Enter Select • Esc Close
            </small>
          </div>
        </div>
      )}

      {/* Search Hints */}
      {mode !== 'simple' && (
        <div className="search-hints">
          {mode === 'phrase' && (
            <small>💡 Searches for exact phrase match</small>
          )}
          {mode === 'boolean' && (
            <small>💡 Use: temperature AND control, sensor OR actuator</small>
          )}
          {mode === 'wildcard' && (
            <small>💡 Use * for prefix: temp* → temperature, temporal</small>
          )}
        </div>
      )}
    </div>
  );
}
