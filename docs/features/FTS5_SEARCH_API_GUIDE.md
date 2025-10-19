# FTS5 Full-Text Search API - User Guide

**Version:** 2.0.0
**Last Updated:** 2025-10-19
**Base URL:** `http://localhost:9123/api/search`

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Search Query Syntax](#search-query-syntax)
4. [Response Format](#response-format)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Basic Search Example

```bash
# Search for 'temperature'
curl "http://localhost:9123/api/search/fulltext?q=temperature&limit=10"
```

**Response:**
```json
{
  "query": "temperature",
  "total_results": 44,
  "results": [
    {
      "id": 123,
      "term": "Room Temperature",
      "definitions": [...],
      "language": "en",
      "source": "internal",
      "relevance_score": -6.2088,
      "snippet": "The ambient temperature in a controlled environment..."
    }
  ]
}
```

---

## 📡 API Endpoints

### 1. Full-Text Search

**Endpoint:** `GET /api/search/fulltext`

Search glossary entries with BM25 ranking and optional filtering.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `q` | string | ✅ Yes | Search query (2-200 chars) | `temperature` |
| `language` | string | ❌ No | Filter by language (en/de) | `en` |
| `domain` | string | ❌ No | Filter by domain tag | `automation` |
| `limit` | integer | ❌ No | Max results (1-500, default: 50) | `10` |
| `offset` | integer | ❌ No | Skip results (default: 0) | `20` |

#### Query Syntax

| Feature | Syntax | Example |
|---------|--------|---------|
| Simple search | `word` | `temperature` |
| Phrase search | `"exact phrase"` | `"temperature control"` |
| Boolean AND | `word1 AND word2` | `temperature AND control` |
| Boolean OR | `word1 OR word2` | `sensor OR actuator` |
| Boolean NOT | `word1 NOT word2` | `temperature NOT sensor` |
| Wildcard prefix | `prefix*` | `temp*` → temperature, temporal |

#### Response

```typescript
{
  query: string;              // The search query
  total_results: number;      // Total matching entries
  results: Array<{
    id: number;
    term: string;
    definitions: Array<object>;
    language: string;         // "en" or "de"
    source: string;
    domain_tags: Array<string>;
    relevance_score: number;  // Lower = better (BM25)
    snippet: string | null;   // First 100 chars of definition
  }>;
  filters_applied: {
    language: string | null;
    domain: string | null;
    limit: number;
    offset: number;
  };
}
```

---

### 2. Search Suggestions (Autocomplete)

**Endpoint:** `GET /api/search/suggest`

Get autocomplete suggestions based on partial term input.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `q` | string | ✅ Yes | Partial term (2-50 chars) | `temp` |
| `language` | string | ❌ No | Filter by language | `en` |
| `limit` | integer | ❌ No | Max suggestions (1-50, default: 10) | `5` |

#### Example Request

```bash
curl "http://localhost:9123/api/search/suggest?q=temp&limit=5"
```

#### Response

```json
{
  "query": "temp",
  "suggestions": [
    "Room Temperature",
    "A Process Temperature",
    "The Temperature",
    "Increasing Temperature",
    "Temperature"
  ]
}
```

---

### 3. Search Statistics

**Endpoint:** `GET /api/search/stats`

Get statistics about the FTS5 search index.

#### Example Request

```bash
curl "http://localhost:9123/api/search/stats"
```

#### Response

```json
{
  "fts5_enabled": true,
  "total_indexed_entries": 2230,
  "entries_by_language": {
    "en": 3312
  },
  "top_sources": {
    "internal": 3312
  },
  "search_features": {
    "porter_stemming": true,
    "diacritic_removal": true,
    "phrase_search": true,
    "wildcard_search": true,
    "boolean_operators": true,
    "bm25_ranking": true,
    "snippet_extraction": true
  }
}
```

---

## 🔍 Search Query Syntax

### 1. Simple Search

Search for a single term. FTS5 automatically applies Porter stemming.

```bash
# Find entries containing "control"
GET /api/search/fulltext?q=control

# Matches: control, controlled, controlling, controller, etc.
```

### 2. Phrase Search

Search for an exact phrase using double quotes.

```bash
# Find exact phrase "temperature control"
GET /api/search/fulltext?q="temperature control"

# Only matches entries with both words adjacent
```

### 3. Boolean AND

Find entries containing ALL terms.

```bash
# Entries must contain both "temperature" AND "control"
GET /api/search/fulltext?q=temperature AND control

# More restrictive than simple search
```

### 4. Boolean OR

Find entries containing ANY of the terms.

```bash
# Entries with "sensor" OR "actuator" (or both)
GET /api/search/fulltext?q=sensor OR actuator

# More results than AND
```

### 5. Boolean NOT

Exclude entries containing a term.

```bash
# Entries with "temperature" but NOT "sensor"
GET /api/search/fulltext?q=temperature NOT sensor
```

### 6. Wildcard Search

Use asterisk (*) for prefix matching.

```bash
# Find all terms starting with "temp"
GET /api/search/fulltext?q=temp*

# Matches: temperature, temporal, template, etc.
```

### 7. Complex Boolean Queries

Combine operators using parentheses.

```bash
# Complex query with grouping
GET /api/search/fulltext?q=process AND (control OR temperature)

# Matches entries with "process" AND either "control" or "temperature"
```

---

## 📦 Response Format

### Search Result Object

```typescript
interface SearchResult {
  id: number;                    // Glossary entry ID
  term: string;                  // The terminology term
  definitions: Definition[];     // Array of definitions
  language: string;              // "en" or "de"
  source: string;                // e.g., "internal", "NAMUR", "DIN"
  domain_tags: string[];         // Domain classifications
  relevance_score: number;       // BM25 score (lower = better)
  snippet: string | null;        // Preview text (100 chars)
}

interface Definition {
  text: string;                  // Definition text
  source_document?: string;      // Source document reference
  page_numbers?: number[];       // Page numbers where found
}
```

### Relevance Score (BM25)

- **Lower scores = better matches** (more relevant)
- Typical range: -10.0 to -1.0
- Considers:
  - Term frequency (how often term appears)
  - Document frequency (how rare the term is)
  - Document length normalization

**Example:**
```
Score: -7.72 → Highly relevant
Score: -4.50 → Moderately relevant
Score: -1.20 → Less relevant
```

---

## 💻 Code Examples

### JavaScript/TypeScript (Fetch API)

```typescript
// Simple search
async function searchGlossary(query: string, limit = 10) {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString()
  });

  const response = await fetch(
    `http://localhost:9123/api/search/fulltext?${params}`
  );

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
}

// Usage
const results = await searchGlossary('temperature', 10);
console.log(`Found ${results.total_results} results`);
results.results.forEach(result => {
  console.log(`${result.term} (score: ${result.relevance_score})`);
});
```

### JavaScript (with Language Filter)

```javascript
// Search with language filter
async function searchEnglishTerms(query) {
  const params = new URLSearchParams({
    q: query,
    language: 'en',
    limit: '20'
  });

  const response = await fetch(
    `http://localhost:9123/api/search/fulltext?${params}`
  );

  return await response.json();
}
```

### Autocomplete Suggestions

```typescript
// Autocomplete component
async function getAutocompleteSuggestions(
  partialTerm: string
): Promise<string[]> {
  if (partialTerm.length < 2) return [];

  const params = new URLSearchParams({
    q: partialTerm,
    limit: '10'
  });

  const response = await fetch(
    `http://localhost:9123/api/search/suggest?${params}`
  );

  const data = await response.json();
  return data.suggestions;
}

// Usage in input handler
inputElement.addEventListener('input', async (e) => {
  const value = e.target.value;
  const suggestions = await getAutocompleteSuggestions(value);
  // Display suggestions in dropdown
});
```

### Python (requests library)

```python
import requests

def search_glossary(query: str, language: str = None, limit: int = 10):
    """Search glossary using FTS5"""
    params = {
        'q': query,
        'limit': limit
    }

    if language:
        params['language'] = language

    response = requests.get(
        'http://localhost:9123/api/search/fulltext',
        params=params
    )

    response.raise_for_status()
    return response.json()

# Usage
results = search_glossary('temperature', language='en', limit=20)
print(f"Found {results['total_results']} results")

for result in results['results']:
    print(f"{result['term']} - Score: {result['relevance_score']:.2f}")
```

### React Component Example

```typescript
import React, { useState, useEffect } from 'react';

interface SearchResult {
  id: number;
  term: string;
  snippet: string;
  relevance_score: number;
}

export function GlossarySearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (query.length < 2) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: query,
        limit: '20'
      });

      const response = await fetch(
        `http://localhost:9123/api/search/fulltext?${params}`
      );

      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Search glossary..."
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>

      <div className="results">
        {results.map(result => (
          <div key={result.id} className="result-item">
            <h3>{result.term}</h3>
            <p>{result.snippet}</p>
            <small>Relevance: {result.relevance_score.toFixed(2)}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## ✅ Best Practices

### 1. Query Optimization

**✅ DO:**
- Use specific terms for better results
- Combine Boolean operators for precision
- Use language filters when targeting specific language
- Implement debouncing for autocomplete (300ms delay)

**❌ DON'T:**
- Use overly generic terms (e.g., "the", "and")
- Create queries longer than 200 characters
- Make autocomplete requests on every keystroke

### 2. Pagination

For large result sets, use `limit` and `offset`:

```javascript
// Page 1: First 20 results
GET /api/search/fulltext?q=control&limit=20&offset=0

// Page 2: Next 20 results
GET /api/search/fulltext?q=control&limit=20&offset=20

// Page 3: Next 20 results
GET /api/search/fulltext?q=control&limit=20&offset=40
```

### 3. Performance Tips

- **Cache search statistics** - Call `/stats` once on app load
- **Debounce autocomplete** - Wait 300ms after user stops typing
- **Use appropriate limits** - Don't request more results than needed
- **Filter early** - Apply language/domain filters when possible

### 4. Error Handling

```typescript
async function safeSearch(query: string) {
  try {
    const response = await fetch(
      `http://localhost:9123/api/search/fulltext?q=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
      if (response.status === 400) {
        // Invalid query syntax
        const error = await response.json();
        console.error('Invalid query:', error.detail);
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Search failed:', error);
    return null;
  }
}
```

---

## 🔧 Troubleshooting

### Issue: No Results Found

**Possible Causes:**
1. Query too specific - Try broader terms
2. Spelling errors - Check term spelling
3. Wrong language filter - Remove or change language parameter
4. Phrase search too restrictive - Use simple search instead

**Solutions:**
```bash
# Too specific
GET /api/search/fulltext?q="exact temperature control system"

# Better - broader query
GET /api/search/fulltext?q=temperature control
```

### Issue: Too Many Results

**Solutions:**
1. Use Boolean AND to narrow results
2. Add language or domain filters
3. Use phrase search for exact matches

```bash
# Narrow with AND
GET /api/search/fulltext?q=temperature AND control

# Add language filter
GET /api/search/fulltext?q=temperature&language=en
```

### Issue: Invalid Query Error (400)

**Common Causes:**
- Unbalanced quotes: `"temperature control`
- Invalid Boolean syntax: `temperature AND AND control`
- Special characters: `temperature&control`

**Solutions:**
- Always close quotes
- Check Boolean operator syntax
- URL-encode special characters

### Issue: Slow Response Time

**Possible Causes:**
1. Very broad wildcard search (`a*`, `t*`)
2. Network latency
3. Database locked

**Solutions:**
- Use more specific prefixes for wildcards
- Check network connection
- Reduce concurrent requests

---

## 📊 Performance Characteristics

### Response Times (3,312 entries)

| Query Type | Avg Response Time | Results |
|------------|------------------|---------|
| Simple search | ~0.2 ms | 19-250 |
| Boolean AND | ~0.2 ms | 2-10 |
| Wildcard | ~0.2-6 ms | 48-2977 |
| Filtered | ~0.2 ms | 44 |

### Scaling Characteristics

FTS5 performance scales well with dataset size:
- **3K entries:** 0.2ms average
- **10K entries:** 0.5ms average (estimated)
- **100K entries:** 2-5ms average (estimated)

**Note:** LIKE queries would be 10-20x slower at each scale.

---

## 🆘 Support & Resources

### Documentation
- FTS5 Implementation: `docs/FTS5_IMPLEMENTATION_COMPLETE.md`
- Performance Benchmarks: `docs/FTS5_PERFORMANCE_BENCHMARKS.md`
- SQLite FTS5 Docs: https://www.sqlite.org/fts5.html

### API Testing
- OpenAPI/Swagger UI: http://localhost:9123/docs
- ReDoc: http://localhost:9123/redoc

### Example Queries
```bash
# 1. Find all temperature-related terms
GET /api/search/fulltext?q=temp*&limit=50

# 2. Search German translations
GET /api/search/fulltext?q=temperature&language=de

# 3. Complex technical search
GET /api/search/fulltext?q=process AND (control OR automation)

# 4. Get top 5 autocomplete suggestions
GET /api/search/suggest?q=sen&limit=5
```

---

**API Version:** 2.0.0
**Last Updated:** 2025-10-19
**Maintained by:** Glossary Application Team
