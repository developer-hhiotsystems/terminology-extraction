import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import apiClient from '../api/client';
import type { SearchResult, SearchFilters, SearchMode } from '../types/search';

interface UseSearchOptions {
  initialQuery?: string;
  initialMode?: SearchMode;
  initialFilters?: SearchFilters;
  debounceMs?: number;
}

export function useSearch(options: UseSearchOptions = {}) {
  const {
    initialQuery = '',
    initialMode = 'simple',
    initialFilters = {},
    debounceMs = 300,
  } = options;

  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize from URL if available
  const urlQuery = searchParams.get('q') || initialQuery;
  const urlMode = (searchParams.get('mode') as SearchMode) || initialMode;
  const urlLanguage = searchParams.get('language') || initialFilters.language;

  const [query, setQuery] = useState(urlQuery);
  const [mode, setMode] = useState<SearchMode>(urlMode);
  const [filters, setFilters] = useState<SearchFilters>({
    ...initialFilters,
    language: urlLanguage,
  });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const debounceTimerRef = useRef<NodeJS.Timeout>();

  // Sync state to URL
  const updateURL = useCallback((q: string, m: SearchMode, f: SearchFilters) => {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (m !== 'simple') params.set('mode', m);
    if (f.language) params.set('language', f.language);
    if (f.domain) params.set('domain', f.domain);
    setSearchParams(params);
  }, [setSearchParams]);

  // Format query based on mode
  const formatQuery = useCallback((q: string, m: SearchMode): string => {
    if (!q.trim()) return q;

    switch (m) {
      case 'phrase':
        // Wrap in quotes if not already
        return q.startsWith('"') ? q : `"${q}"`;
      case 'wildcard':
        // Add asterisk if not already present
        return q.endsWith('*') ? q : `${q}*`;
      case 'boolean':
        // Return as-is, user controls AND/OR/NOT
        return q;
      case 'simple':
      default:
        return q;
    }
  }, []);

  // Perform search
  const performSearch = useCallback(async (
    searchQuery: string,
    searchMode: SearchMode,
    searchFilters: SearchFilters
  ) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setTotalResults(0);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formattedQuery = formatQuery(searchQuery, searchMode);
      const response = await apiClient.searchFulltext({
        q: formattedQuery,
        ...searchFilters,
        limit: searchFilters.limit || 50,
        offset: searchFilters.offset || 0,
      });

      setResults(response.results);
      setTotalResults(response.total_results);
      updateURL(searchQuery, searchMode, searchFilters);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  }, [formatQuery, updateURL]);

  // Debounced search
  const debouncedSearch = useCallback((
    q: string,
    m: SearchMode,
    f: SearchFilters
  ) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      performSearch(q, m, f);
    }, debounceMs);
  }, [performSearch, debounceMs]);

  // Get autocomplete suggestions
  const getSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await apiClient.searchSuggest({
        q,
        language: filters.language,
        limit: 8,
      });
      setSuggestions(response.suggestions);
      setShowSuggestions(response.suggestions.length > 0);
    } catch (err) {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [filters.language]);

  // Debounced autocomplete
  useEffect(() => {
    if (mode === 'simple' && query.length >= 2) {
      const timer = setTimeout(() => {
        getSuggestions(query);
      }, debounceMs);

      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query, mode, getSuggestions, debounceMs]);

  // Handle query change
  const handleQueryChange = useCallback((newQuery: string) => {
    setQuery(newQuery);
  }, []);

  // Handle mode change
  const handleModeChange = useCallback((newMode: SearchMode) => {
    setMode(newMode);
    if (query.trim()) {
      debouncedSearch(query, newMode, filters);
    }
  }, [query, filters, debouncedSearch]);

  // Handle filter change
  const handleFilterChange = useCallback((newFilters: Partial<SearchFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    if (query.trim()) {
      debouncedSearch(query, mode, updatedFilters);
    }
  }, [query, mode, filters, debouncedSearch]);

  // Handle search submit (immediate, no debounce)
  const handleSearchSubmit = useCallback(() => {
    performSearch(query, mode, filters);
    setShowSuggestions(false);
  }, [query, mode, filters, performSearch]);

  // Handle suggestion select
  const handleSuggestionSelect = useCallback((suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    performSearch(suggestion, mode, filters);
  }, [mode, filters, performSearch]);

  // Clear search
  const clearSearch = useCallback(() => {
    setQuery('');
    setResults([]);
    setTotalResults(0);
    setError(null);
    setSuggestions([]);
    setShowSuggestions(false);
    setSearchParams({});
  }, [setSearchParams]);

  return {
    // State
    query,
    mode,
    filters,
    results,
    totalResults,
    loading,
    error,
    suggestions,
    showSuggestions,

    // Actions
    setQuery: handleQueryChange,
    setMode: handleModeChange,
    setFilters: handleFilterChange,
    search: handleSearchSubmit,
    selectSuggestion: handleSuggestionSelect,
    clearSearch,
    hideSuggestions: () => setShowSuggestions(false),
  };
}
