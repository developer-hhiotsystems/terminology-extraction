import { useState, useEffect, useRef } from 'react'
import { toast } from 'react-toastify'
import { saveAs } from 'file-saver'
import Papa from 'papaparse'
import apiClient from '../api/client'
import type { GlossaryEntry } from '../types'
import GlossaryEntryForm from './GlossaryEntryForm'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'

export default function GlossaryList() {
  const [entries, setEntries] = useState<GlossaryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [languageFilter, setLanguageFilter] = useState<string>('')
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingEntry, setEditingEntry] = useState<GlossaryEntry | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; term: string } | null>(null)
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const [resetting, setResetting] = useState(false)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [totalCount, setTotalCount] = useState(0)

  const searchInputRef = useRef<HTMLInputElement>(null)

  // Keyboard shortcuts for this component
  useKeyboardShortcuts({
    onAddEntry: () => setShowForm(true),
    onFocusSearch: () => searchInputRef.current?.focus(),
    onCloseModal: () => {
      if (showForm) {
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

      const data = await apiClient.getGlossaryEntries(params)
      setEntries(data)

      // Get total count with filters applied
      // For accurate count with combined filters, we need to query with limit=0 or use stats
      if (languageFilter || sourceFilter) {
        // Fetch count by making a query with high limit to get accurate total
        const countParams = { ...params, skip: 0, limit: 10000 }
        const allFiltered = await apiClient.getGlossaryEntries(countParams)
        setTotalCount(allFiltered.length)
      } else {
        // No filters, use stats for efficiency
        const stats = await apiClient.getDatabaseStats()
        setTotalCount(stats.total_glossary_entries || stats.total_entries || 0)
      }

      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load glossary entries')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setCurrentPage(1)
      fetchEntries()
      return
    }

    try {
      setLoading(true)
      const data = await apiClient.searchGlossary(searchQuery, languageFilter)
      setEntries(data)
      setTotalCount(data.length)
      setCurrentPage(1)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setLoading(false)
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

  const handleExportCSV = () => {
    if (entries.length === 0) {
      toast.warning('No entries to export')
      return
    }

    const csvData = entries.map(entry => ({
      ID: entry.id,
      Term: entry.term,
      Definition: entry.definition,
      Language: entry.language,
      Source: entry.source,
      'Domain Tags': entry.domain_tags?.join('; ') || '',
      'Validation Status': entry.validation_status,
      'Sync Status': entry.sync_status,
      'Created': entry.creation_date,
      'Updated': entry.updated_at
    }))

    const csv = Papa.unparse(csvData)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const timestamp = new Date().toISOString().split('T')[0]
    saveAs(blob, `glossary-export-${timestamp}.csv`)
    toast.success(`Exported ${entries.length} entries to CSV`)
  }

  const handleExportJSON = () => {
    if (entries.length === 0) {
      toast.warning('No entries to export')
      return
    }

    const json = JSON.stringify(entries, null, 2)
    const blob = new Blob([json], { type: 'application/json;charset=utf-8;' })
    const timestamp = new Date().toISOString().split('T')[0]
    saveAs(blob, `glossary-export-${timestamp}.json`)
    toast.success(`Exported ${entries.length} entries to JSON`)
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

  useEffect(() => {
    setCurrentPage(1)
    fetchEntries()
  }, [languageFilter, sourceFilter])

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
          <button
            className="btn-danger"
            onClick={() => setShowResetConfirm(true)}
            title="Reset entire database"
          >
            Reset DB
          </button>
          <button className="btn-secondary" onClick={handleExportCSV} disabled={entries.length === 0}>
            Export CSV
          </button>
          <button className="btn-secondary" onClick={handleExportJSON} disabled={entries.length === 0}>
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
        <div className="search-box">
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search terms... (Press / to focus)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            title="Press / to focus this field"
          />
          <button onClick={handleSearch}>Search</button>
        </div>

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
      </div>

      {totalCount > 0 && <PaginationControls />}

      {entries.length === 0 ? (
        <div className="empty-state">
          <p>No glossary entries found.</p>
          <p>Upload a PDF or create an entry manually.</p>
        </div>
      ) : (
        <div className="entries-grid">
          {entries.map((entry) => (
            <div key={entry.id} className="entry-card">
              <div className="entry-header">
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

              <p className="entry-definition">{entry.definition}</p>

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
                  <li>All glossary entries ({entries.length} entries)</li>
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
