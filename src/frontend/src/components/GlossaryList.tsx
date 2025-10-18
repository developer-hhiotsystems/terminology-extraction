import { useState, useEffect, useRef, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { toast } from 'react-toastify'
import { saveAs } from 'file-saver'
import apiClient from '../api/client'
import type { GlossaryEntry } from '../types'
import GlossaryEntryForm from './GlossaryEntryForm'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'

export default function GlossaryList() {
  const location = useLocation()
  const [entries, setEntries] = useState<GlossaryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [languageFilter, setLanguageFilter] = useState<string>('')
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [validationFilter, setValidationFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingEntry, setEditingEntry] = useState<GlossaryEntry | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; term: string } | null>(null)
  const [bulkDeleteConfirm, setBulkDeleteConfirm] = useState(false)
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [isSearchActive, setIsSearchActive] = useState(false)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [totalCount, setTotalCount] = useState(0)

  // Bulk selection state
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  // Autocomplete state
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1)
  const [allTerms, setAllTerms] = useState<string[]>([])

  // Quick actions menu state
  const [quickActionsEntry, setQuickActionsEntry] = useState<number | null>(null)
  const [quickActionsPosition, setQuickActionsPosition] = useState({ x: 0, y: 0 })

  const searchInputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const quickActionsRef = useRef<HTMLDivElement>(null)

  // Load all terms for autocomplete (limited to 1000 per API constraint)
  const loadAllTerms = useCallback(async () => {
    try {
      const allEntries = await apiClient.getGlossaryEntries({ skip: 0, limit: 1000 })
      const terms = allEntries.map((e: GlossaryEntry) => e.term)
      setAllTerms(terms)
    } catch (err) {
      // Silent fail for autocomplete
      console.error('Failed to load terms for autocomplete:', err)
    }
  }, [])

  // Debounced autocomplete suggestions
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    const timer = setTimeout(() => {
      const query = searchQuery.toLowerCase()
      const matches = allTerms
        .filter(term => term.toLowerCase().includes(query))
        .slice(0, 8) // Limit to 8 suggestions

      setSuggestions(matches)
      setShowSuggestions(matches.length > 0)
      setSelectedSuggestion(-1)
    }, 300) // 300ms debounce

    return () => clearTimeout(timer)
  }, [searchQuery, allTerms])

  // Close suggestions and quick actions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node) &&
          searchInputRef.current && !searchInputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false)
      }

      if (quickActionsRef.current && !quickActionsRef.current.contains(e.target as Node)) {
        setQuickActionsEntry(null)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Keyboard shortcuts for this component
  useKeyboardShortcuts({
    onAddEntry: () => setShowForm(true),
    onFocusSearch: () => searchInputRef.current?.focus(),
    onCloseModal: () => {
      if (showSuggestions) {
        setShowSuggestions(false)
      } else if (showForm) {
        setShowForm(false)
        setEditingEntry(null)
      } else if (deleteConfirm) {
        setDeleteConfirm(null)
      } else if (showResetConfirm) {
        setShowResetConfirm(false)
      }
    },
  })

  const fetchEntries = async () => {
    try {
      setLoading(true)
      const params: any = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      }
      if (languageFilter) params.language = languageFilter
      if (sourceFilter) params.source = sourceFilter
      if (validationFilter) params.validation_status = validationFilter

      const data = await apiClient.getGlossaryEntries(params)
      setEntries(data)

      // Get total count with filters applied
      // For accurate count with combined filters, we need to query with limit=0 or use stats
      if (languageFilter || sourceFilter || validationFilter) {
        // Fetch count by making a query with max limit (1000 per API constraint)
        const countParams = { ...params, skip: 0, limit: 1000 }
        const allFiltered = await apiClient.getGlossaryEntries(countParams)
        setTotalCount(allFiltered.length)
      } else {
        // No filters, use stats for efficiency
        const stats = await apiClient.getDatabaseStats()
        setTotalCount(stats.total_glossary_entries || stats.total_entries || 0)
      }

      setError(null)
    } catch (err: any) {
      // Handle validation errors (422) that return arrays of error objects
      let errorMessage = 'Failed to load glossary entries'
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          // FastAPI validation errors return array of objects
          errorMessage = err.response.data.detail
            .map((e: any) => `${e.loc?.join('.')} - ${e.msg}`)
            .join(', ')
        } else {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      }
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (query?: string) => {
    const searchTerm = query ?? searchQuery
    if (!searchTerm.trim()) {
      handleClearSearch()
      return
    }

    try {
      setLoading(true)
      const data = await apiClient.searchGlossary(searchTerm, languageFilter)
      setEntries(data)
      setTotalCount(data.length)
      setCurrentPage(1)
      setError(null)
      setShowSuggestions(false)
      setIsSearchActive(true)
      toast.info(`Found ${data.length} entries matching "${searchTerm}"`)
    } catch (err: any) {
      // Handle validation errors (422) that return arrays of error objects
      let errorMessage = 'Search failed'
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          // FastAPI validation errors return array of objects
          errorMessage = err.response.data.detail
            .map((e: any) => `${e.loc?.join('.')} - ${e.msg}`)
            .join(', ')
        } else {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      }
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setIsSearchActive(false)
    setCurrentPage(1)
    fetchEntries()
    toast.info('Search cleared')
  }

  const handleSuggestionSelect = (term: string) => {
    setSearchQuery(term)
    setShowSuggestions(false)
    handleSearch(term)
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) {
      if (e.key === 'Enter') {
        handleSearch()
      }
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedSuggestion(prev =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedSuggestion(prev => (prev > 0 ? prev - 1 : -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedSuggestion >= 0 && selectedSuggestion < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedSuggestion])
        } else {
          handleSearch()
        }
        break
      case 'Escape':
        setShowSuggestions(false)
        setSelectedSuggestion(-1)
        break
    }
  }

  const handleDelete = async (id: number, term: string) => {
    setDeleteConfirm({ id, term })
  }

  const confirmDelete = async () => {
    if (!deleteConfirm) return

    try {
      await apiClient.deleteGlossaryEntry(deleteConfirm.id)
      toast.success('Entry deleted successfully')
      setDeleteConfirm(null)
      fetchEntries()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete entry')
      setDeleteConfirm(null)
    }
  }

  const handleEdit = (entry: GlossaryEntry) => {
    setEditingEntry(entry)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingEntry(null)
    fetchEntries()
  }

  const handleExport = async (format: 'csv' | 'excel' | 'json') => {
    try {
      const params: any = {}
      if (languageFilter) params.language = languageFilter
      if (sourceFilter) params.source = sourceFilter
      if (validationFilter) params.validation_status = validationFilter

      const blob = await apiClient.exportGlossary(format, params)
      const timestamp = new Date().toISOString().split('T')[0]
      const extension = format === 'excel' ? 'xlsx' : format
      saveAs(blob, `glossary-export-${timestamp}.${extension}`)
      toast.success(`Exported to ${format.toUpperCase()} successfully`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || `Failed to export to ${format.toUpperCase()}`)
    }
  }

  const handleSelectAll = () => {
    if (selectedIds.size === entries.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(entries.map(e => e.id)))
    }
  }

  const handleSelectEntry = (id: number) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }


  const handleResetDatabase = async () => {
    setResetting(true)
    try {
      const result = await apiClient.resetDatabase()
      toast.success(result.message)
      setShowResetConfirm(false)
      fetchEntries()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to reset database')
    } finally {
      setResetting(false)
    }
  }

  const handleQuickAction = (entry: GlossaryEntry, action: string) => {
    setQuickActionsEntry(null)

    switch (action) {
      case 'edit':
        handleEdit(entry)
        break
      case 'delete':
        handleDelete(entry.id, entry.term)
        break
      case 'copy':
        navigator.clipboard.writeText(entry.term)
        toast.success(`Copied "${entry.term}" to clipboard`)
        break
      case 'validate':
        handleBulkUpdate('validated', [entry.id])
        break
      case 'reject':
        handleBulkUpdate('rejected', [entry.id])
        break
      case 'pending':
        handleBulkUpdate('pending', [entry.id])
        break
    }
  }

  const handleBulkUpdate = async (status: 'validated' | 'rejected' | 'pending', ids?: number[]) => {
    const targetIds = ids || Array.from(selectedIds)
    if (targetIds.length === 0) {
      toast.warning('No entries selected')
      return
    }

    try {
      const result = await apiClient.bulkUpdateEntries(targetIds, status)
      toast.success(result.message)
      if (!ids) setSelectedIds(new Set())
      fetchEntries()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update entries')
    }
  }

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) {
      toast.warning('No entries selected')
      return
    }

    try {
      const deletePromises = Array.from(selectedIds).map(id =>
        apiClient.deleteGlossaryEntry(id)
      )
      await Promise.all(deletePromises)

      toast.success(`Successfully deleted ${selectedIds.size} entries`)
      setSelectedIds(new Set())
      setBulkDeleteConfirm(false)
      fetchEntries()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete entries')
      setBulkDeleteConfirm(false)
    }
  }

  const handleShowQuickActions = (e: React.MouseEvent, entryId: number) => {
    e.preventDefault()
    e.stopPropagation()

    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
    setQuickActionsPosition({
      x: rect.right - 200, // Position menu to the left of the button
      y: rect.bottom + 5
    })
    setQuickActionsEntry(entryId)
  }

  useEffect(() => {
    loadAllTerms()
  }, [loadAllTerms])

  // Handle validation filter from navigation state (from Statistics page)
  useEffect(() => {
    const state = location.state as { validationFilter?: string } | null
    if (state?.validationFilter) {
      setValidationFilter(state.validationFilter)
      toast.info(`Filtering by ${state.validationFilter} entries`)
      // Clear the state to avoid re-applying filter on refresh
      window.history.replaceState({}, document.title)
    }
  }, [location])

  useEffect(() => {
    setCurrentPage(1)
    fetchEntries()
  }, [languageFilter, sourceFilter, validationFilter])

  useEffect(() => {
    fetchEntries()
  }, [currentPage, pageSize])

  const totalPages = Math.ceil(totalCount / pageSize)
  const startEntry = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1
  const endEntry = Math.min(currentPage * pageSize, totalCount)

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize)
    setCurrentPage(1)
  }

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  const handleFirstPage = () => {
    setCurrentPage(1)
  }

  const handleLastPage = () => {
    setCurrentPage(totalPages)
  }

  const PaginationControls = () => (
    <div className="pagination-controls">
      <div className="pagination-info">
        <span className="entry-count">
          Showing {startEntry}-{endEntry} of {totalCount} entries
        </span>
        <div className="page-size-selector">
          <label htmlFor="pageSize">Show:</label>
          <select
            id="pageSize"
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
          <span>per page</span>
        </div>
      </div>
      <div className="pagination-buttons">
        <button
          className="btn-pagination"
          onClick={handleFirstPage}
          disabled={currentPage === 1 || loading}
          title="First page"
        >
          «
        </button>
        <button
          className="btn-pagination"
          onClick={handlePreviousPage}
          disabled={currentPage === 1 || loading}
          title="Previous page"
        >
          ‹
        </button>
        <span className="page-indicator">
          Page {currentPage} of {totalPages || 1}
        </span>
        <button
          className="btn-pagination"
          onClick={handleNextPage}
          disabled={currentPage >= totalPages || loading}
          title="Next page"
        >
          ›
        </button>
        <button
          className="btn-pagination"
          onClick={handleLastPage}
          disabled={currentPage >= totalPages || loading}
          title="Last page"
        >
          »
        </button>
      </div>
    </div>
  )

  if (loading) return <div className="loading">Loading glossary entries...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="glossary-list">
      <div className="glossary-header">
        <h2>Glossary Entries ({totalCount})</h2>
        <div className="header-actions">
          {selectedIds.size > 0 && (
            <div className="bulk-actions">
              <span className="selected-count">{selectedIds.size} selected</span>
              <button
                className="btn-success"
                onClick={() => handleBulkUpdate('validated')}
                title="Mark selected as validated"
              >
                ✓ Validate
              </button>
              <button
                className="btn-danger"
                onClick={() => handleBulkUpdate('rejected')}
                title="Mark selected as rejected"
              >
                ✗ Reject
              </button>
              <button
                className="btn-danger"
                onClick={() => setBulkDeleteConfirm(true)}
                title="Delete selected entries"
              >
                🗑️ Delete
              </button>
              <button
                className="btn-secondary"
                onClick={() => setSelectedIds(new Set())}
                title="Clear selection"
              >
                Clear
              </button>
            </div>
          )}
          <button
            className="btn-danger"
            onClick={() => setShowResetConfirm(true)}
            title="Reset entire database"
          >
            Reset DB
          </button>
          <button className="btn-secondary" onClick={() => handleExport('csv')} disabled={totalCount === 0}>
            Export CSV
          </button>
          <button className="btn-secondary" onClick={() => handleExport('excel')} disabled={totalCount === 0}>
            Export Excel
          </button>
          <button className="btn-secondary" onClick={() => handleExport('json')} disabled={totalCount === 0}>
            Export JSON
          </button>
          <button
            className="btn-primary"
            onClick={() => setShowForm(true)}
            title="Add new entry (Ctrl+N or Cmd+N)"
          >
            + Add Entry
          </button>
        </div>
      </div>

      <div className="filters">
        <form
          className="search-box autocomplete-container"
          onSubmit={(e) => {
            e.preventDefault()
            handleSearch()
          }}
        >
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search terms... (Press / to focus)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            onFocus={() => {
              if (suggestions.length > 0 && searchQuery.length >= 2) {
                setShowSuggestions(true)
              }
            }}
            title="Press / to focus this field"
            autoComplete="off"
          />
          {isSearchActive ? (
            <button
              type="button"
              className="btn-secondary"
              onClick={handleClearSearch}
              title="Clear search and show all entries"
            >
              ✕ Clear
            </button>
          ) : (
            <button type="submit">Search</button>
          )}

          {showSuggestions && suggestions.length > 0 && (
            <div ref={suggestionsRef} className="autocomplete-suggestions">
              {suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className={`suggestion-item ${idx === selectedSuggestion ? 'selected' : ''}`}
                  onClick={() => handleSuggestionSelect(suggestion)}
                  onMouseEnter={() => setSelectedSuggestion(idx)}
                >
                  <span className="suggestion-icon">🔍</span>
                  <span className="suggestion-text">{suggestion}</span>
                </div>
              ))}
            </div>
          )}
        </form>

        <select
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
        >
          <option value="">All Languages</option>
          <option value="en">English</option>
          <option value="de">German</option>
        </select>

        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
        >
          <option value="">All Sources</option>
          <option value="internal">Internal</option>
          <option value="NAMUR">NAMUR</option>
          <option value="DIN">DIN</option>
          <option value="ASME">ASME</option>
          <option value="IEC">IEC</option>
          <option value="IATE">IATE</option>
        </select>

        <select
          value={validationFilter}
          onChange={(e) => setValidationFilter(e.target.value)}
          className={validationFilter ? 'filter-active' : ''}
        >
          <option value="">All Statuses</option>
          <option value="validated">✓ Validated</option>
          <option value="pending">⏳ Pending</option>
          <option value="rejected">✗ Rejected</option>
        </select>

        {(languageFilter || sourceFilter || validationFilter) && (
          <button
            className="btn-secondary clear-filters-btn"
            onClick={() => {
              setLanguageFilter('')
              setSourceFilter('')
              setValidationFilter('')
              toast.info('Filters cleared')
            }}
            title="Clear all filters"
          >
            ✕ Clear Filters
          </button>
        )}
      </div>

      {totalCount > 0 && (
        <div className="bulk-select-toolbar">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={selectedIds.size === entries.length && entries.length > 0}
              onChange={handleSelectAll}
            />
            <span>Select All ({entries.length})</span>
          </label>
          {selectedIds.size > 0 && (
            <span className="selection-info">
              {selectedIds.size} of {entries.length} selected on this page
            </span>
          )}
        </div>
      )}

      {totalCount > 0 && <PaginationControls />}

      {entries.length === 0 ? (
        <div className="empty-state">
          <p>No glossary entries found.</p>
          <p>Upload a PDF or create an entry manually.</p>
        </div>
      ) : (
        <div className="entries-grid">
          {entries.map((entry) => (
            <div key={entry.id} className={`entry-card ${selectedIds.has(entry.id) ? 'selected' : ''}`}>
              <div className="entry-header">
                <label className="entry-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(entry.id)}
                    onChange={() => handleSelectEntry(entry.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </label>
                <h3>{entry.term}</h3>
                <div className="entry-badges">
                  <span className={`badge lang-${entry.language}`}>
                    {entry.language.toUpperCase()}
                  </span>
                  <span className={`badge status-${entry.validation_status}`}>
                    {entry.validation_status}
                  </span>
                </div>
              </div>

              <div className="entry-definitions">
                {entry.definitions && entry.definitions.length > 0 ? (
                  entry.definitions.map((def, idx) => {
                    // Parse definition text to separate label from content
                    const parts = def.text.split('\n\n');
                    const hasStructuredFormat = parts.length >= 2 && parts[0].includes('found in context');

                    return (
                      <div key={idx} className={`definition-item ${def.is_primary ? 'primary' : ''}`}>
                        {def.is_primary && <span className="primary-badge">Primary</span>}

                        {hasStructuredFormat ? (
                          <div className="definition-structured">
                            <div className="definition-label">{parts[0]}</div>
                            <div className="definition-context">
                              {parts.slice(1).join('\n\n')}
                            </div>
                          </div>
                        ) : (
                          <p className="definition-text">{def.text}</p>
                        )}

                        <div className="definition-metadata">
                          {def.source_doc_id && (
                            <span className="definition-source" title={`Document ID: ${def.source_doc_id}`}>
                              📄 Doc #{def.source_doc_id}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p className="entry-definition">No definition available</p>
                )}
              </div>

              <div className="entry-meta">
                <span>Source: {entry.source}</span>
                {entry.source_document && (
                  <span>Document: {entry.source_document}</span>
                )}
              </div>

              {entry.domain_tags && entry.domain_tags.length > 0 && (
                <div className="entry-tags">
                  {entry.domain_tags.map((tag, idx) => (
                    <span key={idx} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="entry-actions">
                <button
                  className="btn-quick-actions"
                  onClick={(e) => handleShowQuickActions(e, entry.id)}
                  title="Quick actions"
                >
                  ⋮
                </button>
                <button
                  className="btn-edit"
                  onClick={() => handleEdit(entry)}
                >
                  Edit
                </button>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(entry.id, entry.term)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions Menu */}
      {quickActionsEntry !== null && (
        <div
          ref={quickActionsRef}
          className="quick-actions-menu"
          style={{
            position: 'fixed',
            left: `${quickActionsPosition.x}px`,
            top: `${quickActionsPosition.y}px`,
            zIndex: 1000
          }}
        >
          {(() => {
            const entry = entries.find(e => e.id === quickActionsEntry)
            if (!entry) return null

            return (
              <>
                <div className="quick-actions-header">
                  <span>Quick Actions</span>
                  <button
                    className="quick-actions-close"
                    onClick={() => setQuickActionsEntry(null)}
                  >
                    ✕
                  </button>
                </div>
                <div className="quick-actions-list">
                  <button
                    className="quick-action-item"
                    onClick={() => handleQuickAction(entry, 'edit')}
                  >
                    <span className="action-icon">✏️</span>
                    <span>Edit Entry</span>
                  </button>
                  <button
                    className="quick-action-item"
                    onClick={() => handleQuickAction(entry, 'copy')}
                  >
                    <span className="action-icon">📋</span>
                    <span>Copy Term</span>
                  </button>
                  <div className="quick-actions-divider" />
                  <button
                    className="quick-action-item"
                    onClick={() => handleQuickAction(entry, 'validate')}
                    disabled={entry.validation_status === 'validated'}
                  >
                    <span className="action-icon">✓</span>
                    <span>Mark as Validated</span>
                  </button>
                  <button
                    className="quick-action-item"
                    onClick={() => handleQuickAction(entry, 'pending')}
                    disabled={entry.validation_status === 'pending'}
                  >
                    <span className="action-icon">⏳</span>
                    <span>Mark as Pending</span>
                  </button>
                  <button
                    className="quick-action-item"
                    onClick={() => handleQuickAction(entry, 'reject')}
                    disabled={entry.validation_status === 'rejected'}
                  >
                    <span className="action-icon">✗</span>
                    <span>Mark as Rejected</span>
                  </button>
                  <div className="quick-actions-divider" />
                  <button
                    className="quick-action-item danger"
                    onClick={() => handleQuickAction(entry, 'delete')}
                  >
                    <span className="action-icon">🗑️</span>
                    <span>Delete Entry</span>
                  </button>
                </div>
              </>
            )
          })()}
        </div>
      )}

      {totalCount > 0 && <PaginationControls />}

      {showForm && (
        <GlossaryEntryForm
          entry={editingEntry}
          onClose={handleFormClose}
        />
      )}

      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content delete-confirm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Confirm Delete</h2>
              <button className="close-btn" onClick={() => setDeleteConfirm(null)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to delete this entry?</p>
              <p className="delete-term"><strong>{deleteConfirm.term}</strong></p>
              <p className="warning-text">This action cannot be undone.</p>
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setDeleteConfirm(null)}>
                Cancel
              </button>
              <button className="btn-danger" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {bulkDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setBulkDeleteConfirm(false)}>
          <div className="modal-content delete-confirm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚠️ Confirm Bulk Delete</h2>
              <button className="close-btn" onClick={() => setBulkDeleteConfirm(false)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to delete <strong>{selectedIds.size} selected entries</strong>?</p>
              <p className="warning-text">This action cannot be undone.</p>
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setBulkDeleteConfirm(false)}>
                Cancel
              </button>
              <button className="btn-danger" onClick={handleBulkDelete}>
                Delete {selectedIds.size} Entries
              </button>
            </div>
          </div>
        </div>
      )}

      {showResetConfirm && (
        <div className="modal-overlay" onClick={() => !resetting && setShowResetConfirm(false)}>
          <div className="modal-content reset-confirm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚠️ Reset Database</h2>
              <button className="close-btn" onClick={() => !resetting && setShowResetConfirm(false)} disabled={resetting}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="reset-warning">
                <p className="warning-title">This will permanently delete:</p>
                <ul className="warning-list">
                  <li>All glossary entries ({totalCount} entries)</li>
                  <li>All uploaded documents</li>
                  <li>All uploaded PDF files from disk</li>
                </ul>
                <p className="warning-text-large">
                  This action is <strong>IRREVERSIBLE</strong> and cannot be undone!
                </p>
                <p className="warning-confirm">
                  Are you absolutely sure you want to proceed?
                </p>
              </div>
            </div>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setShowResetConfirm(false)}
                disabled={resetting}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                onClick={handleResetDatabase}
                disabled={resetting}
              >
                {resetting ? 'Resetting...' : 'Yes, Reset Database'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
