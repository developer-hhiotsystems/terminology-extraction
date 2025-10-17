import { useState, useEffect } from 'react'
import apiClient from '../api/client'
import type { GlossaryEntry } from '../types'
import GlossaryEntryForm from './GlossaryEntryForm'

export default function GlossaryList() {
  const [entries, setEntries] = useState<GlossaryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [languageFilter, setLanguageFilter] = useState<string>('')
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingEntry, setEditingEntry] = useState<GlossaryEntry | null>(null)

  const fetchEntries = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (languageFilter) params.language = languageFilter
      if (sourceFilter) params.source = sourceFilter

      const data = await apiClient.getGlossaryEntries(params)
      setEntries(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load glossary entries')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchEntries()
      return
    }

    try {
      setLoading(true)
      const data = await apiClient.searchGlossary(searchQuery, languageFilter)
      setEntries(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this entry?')) return

    try {
      await apiClient.deleteGlossaryEntry(id)
      fetchEntries()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete entry')
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

  useEffect(() => {
    fetchEntries()
  }, [languageFilter, sourceFilter])

  if (loading) return <div className="loading">Loading glossary entries...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="glossary-list">
      <div className="glossary-header">
        <h2>Glossary Entries ({entries.length})</h2>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          + Add Entry
        </button>
      </div>

      <div className="filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
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
                  onClick={() => handleDelete(entry.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <GlossaryEntryForm
          entry={editingEntry}
          onClose={handleFormClose}
        />
      )}
    </div>
  )
}
