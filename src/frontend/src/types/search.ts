// FTS5 Search Types

export interface SearchResult {
  id: number;
  term: string;
  definitions: any[];
  language: string;
  source: string;
  domain_tags: string[];
  relevance_score: number;
  snippet: string | null;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
  filters_applied: {
    language: string | null;
    domain: string | null;
    limit: number;
    offset: number;
  };
}

export interface SearchSuggestion {
  query: string;
  suggestions: string[];
}

export interface SearchStats {
  fts5_enabled: boolean;
  total_indexed_entries: number;
  entries_by_language: Record<string, number>;
  top_sources: Record<string, number>;
  search_features: {
    porter_stemming: boolean;
    diacritic_removal: boolean;
    phrase_search: boolean;
    wildcard_search: boolean;
    boolean_operators: boolean;
    bm25_ranking: boolean;
    snippet_extraction: boolean;
  };
}

export interface SearchFilters {
  language?: string;
  domain?: string;
  limit?: number;
  offset?: number;
}

export type SearchMode = 'simple' | 'phrase' | 'boolean' | 'wildcard';

export interface SearchState {
  query: string;
  mode: SearchMode;
  filters: SearchFilters;
  results: SearchResult[];
  totalResults: number;
  loading: boolean;
  error: string | null;
}
