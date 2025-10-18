import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { UploadedDocument, DocumentType } from '../types'

export default function DocumentList() {
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<UploadedDocument[]>([])
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<number | null>(null)

  // Filter & Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')

  // Bulk operations state
  const [selectedDocs, setSelectedDocs] = useState<Set<number>>(new Set())
  const [bulkDeleting, setBulkDeleting] = useState(false)

  // Edit metadata modal state
  const [editingDoc, setEditingDoc] = useState<UploadedDocument | null>(null)
  const [editFormData, setEditFormData] = useState({
    document_number: '',
    document_type_id: null as number | null,
    document_link: ''
  })
  const [saving, setSaving] = useState(false)

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getDocuments()
      setDocuments(data)
      setFilteredDocuments(data)
      setError(null)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load documents'
      setError(errorMsg)
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const fetchDocumentTypes = async () => {
    try {
      const types = await apiClient.getDocumentTypes()
      setDocumentTypes(types)
    } catch (err) {
      console.error('Failed to load document types:', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
    fetchDocumentTypes()
  }, [])

  // Apply filters whenever search/filter criteria change
  useEffect(() => {
    let filtered = [...documents]

    // Search by filename, document number
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(doc =>
        doc.filename.toLowerCase().includes(query) ||
        doc.document_number?.toLowerCase().includes(query) ||
        doc.document_link?.toLowerCase().includes(query)
      )
    }

    // Filter by status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => doc.upload_status === filterStatus)
    }

    // Filter by document type
    if (filterType !== 'all') {
      filtered = filtered.filter(doc => doc.document_type_id === Number(filterType))
    }

    setFilteredDocuments(filtered)
  }, [searchQuery, filterStatus, filterType, documents])

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    setDeleting(id)
    try {
      await apiClient.deleteDocument(id)
      toast.success('Document deleted successfully')
      fetchDocuments()
      setSelectedDocs(prev => {
        const newSet = new Set(prev)
        newSet.delete(id)
        return newSet
      })
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete document')
    } finally {
      setDeleting(null)
    }
  }

  const handleBulkDelete = async () => {
    if (selectedDocs.size === 0) {
      toast.warning('No documents selected')
      return
    }

    if (!confirm(`Are you sure you want to delete ${selectedDocs.size} document(s)?`)) return

    setBulkDeleting(true)
    try {
      const deletePromises = Array.from(selectedDocs).map(id =>
        apiClient.deleteDocument(id)
      )
      await Promise.all(deletePromises)

      toast.success(`Successfully deleted ${selectedDocs.size} document(s)`)
      setSelectedDocs(new Set())
      fetchDocuments()
    } catch (err: any) {
      toast.error('Failed to delete some documents')
    } finally {
      setBulkDeleting(false)
    }
  }

  const toggleSelectDoc = (id: number) => {
    setSelectedDocs(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const toggleSelectAll = () => {
    if (selectedDocs.size === filteredDocuments.length) {
      setSelectedDocs(new Set())
    } else {
      setSelectedDocs(new Set(filteredDocuments.map(doc => doc.id)))
    }
  }

  const handleEditClick = (doc: UploadedDocument) => {
    setEditingDoc(doc)
    setEditFormData({
      document_number: doc.document_number || '',
      document_type_id: doc.document_type_id || null,
      document_link: doc.document_link || ''
    })
  }

  const handleSaveMetadata = async () => {
    if (!editingDoc) return

    setSaving(true)
    try {
      await apiClient.updateDocument(editingDoc.id, {
        document_number: editFormData.document_number || undefined,
        document_type_id: editFormData.document_type_id || undefined,
        document_link: editFormData.document_link || undefined
      })

      toast.success('Document metadata updated successfully')
      setEditingDoc(null)
      fetchDocuments()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update document')
    } finally {
      setSaving(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  }

  const getDocumentTypeName = (typeId: number | null | undefined) => {
    if (!typeId) return '-'
    const type = documentTypes.find(t => t.id === typeId)
    return type ? `${type.label_en} (${type.label_de})` : '-'
  }

  const clearFilters = () => {
    setSearchQuery('')
    setFilterStatus('all')
    setFilterType('all')
  }

  if (loading) return <div className="loading">Loading documents...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="document-list">
      <div className="document-header">
        <h2>Uploaded Documents ({documents.length})</h2>
        <button
          className="btn-primary"
          onClick={() => (window.location.href = '/upload')}
        >
          + Upload PDF
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="empty-state">
          <p>No documents uploaded yet.</p>
          <p>Upload a PDF to get started with term extraction.</p>
        </div>
      ) : (
        <>
          {/* Search and Filter Bar */}
          <div className="filter-bar">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search by filename, document number, or link..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>

            <div className="filter-controls">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>

              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Types</option>
                {documentTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.label_en}
                  </option>
                ))}
              </select>

              {(searchQuery || filterStatus !== 'all' || filterType !== 'all') && (
                <button onClick={clearFilters} className="btn-secondary-small">
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          {/* Bulk Actions Bar */}
          {selectedDocs.size > 0 && (
            <div className="bulk-actions-bar">
              <span className="selected-count">
                {selectedDocs.size} document(s) selected
              </span>
              <button
                onClick={handleBulkDelete}
                disabled={bulkDeleting}
                className="btn-danger"
              >
                {bulkDeleting ? 'Deleting...' : 'Delete Selected'}
              </button>
              <button
                onClick={() => setSelectedDocs(new Set())}
                className="btn-secondary-small"
              >
                Clear Selection
              </button>
            </div>
          )}

          {/* Results Count */}
          <div className="results-info">
            Showing {filteredDocuments.length} of {documents.length} documents
          </div>

          {/* Documents Table */}
          <div className="documents-table">
            <table>
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedDocs.size === filteredDocuments.length && filteredDocuments.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th>ID</th>
                  <th>Filename</th>
                  <th>Document Number</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Terms</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className={selectedDocs.has(doc.id) ? 'selected-row' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedDocs.has(doc.id)}
                        onChange={() => toggleSelectDoc(doc.id)}
                      />
                    </td>
                    <td>{doc.id}</td>
                    <td className="filename">
                      <Link to={`/documents/${doc.id}`} className="document-link">
                        {doc.filename}
                      </Link>
                    </td>
                    <td>{doc.document_number || '-'}</td>
                    <td className="doc-type">{getDocumentTypeName(doc.document_type_id)}</td>
                    <td>{formatFileSize(doc.file_size)}</td>
                    <td>
                      <span className={`status-badge status-${doc.upload_status}`}>
                        {doc.upload_status}
                      </span>
                    </td>
                    <td className="date-col">{formatDate(doc.uploaded_at)}</td>
                    <td>{doc.processing_metadata?.terms_saved || '-'}</td>
                    <td className="actions-cell">
                      <button
                        className="btn-edit-small"
                        onClick={() => handleEditClick(doc)}
                        title="Edit metadata"
                      >
                        Edit
                      </button>
                      <button
                        className="btn-delete-small"
                        onClick={() => handleDelete(doc.id)}
                        disabled={deleting === doc.id}
                        title="Delete document"
                      >
                        {deleting === doc.id ? '...' : 'Delete'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Edit Metadata Modal */}
      {editingDoc && (
        <div className="modal-overlay" onClick={() => setEditingDoc(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Document Metadata</h3>
              <button
                className="modal-close"
                onClick={() => setEditingDoc(null)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <p className="modal-subtitle">
                Editing: <strong>{editingDoc.filename}</strong>
              </p>

              <div className="form-group">
                <label htmlFor="edit_document_number">Document Number</label>
                <input
                  id="edit_document_number"
                  type="text"
                  value={editFormData.document_number}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, document_number: e.target.value })
                  }
                  placeholder="e.g., DOC-2024-001"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_document_type">Document Type</label>
                <select
                  id="edit_document_type"
                  value={editFormData.document_type_id || ''}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      document_type_id: e.target.value ? Number(e.target.value) : null
                    })
                  }
                  className="form-select"
                >
                  <option value="">-- Select Type --</option>
                  {documentTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.label_en} ({type.label_de})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="edit_document_link">Document Link / Path</label>
                <input
                  id="edit_document_link"
                  type="text"
                  value={editFormData.document_link}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, document_link: e.target.value })
                  }
                  placeholder="https://... or \\server\path\file.pdf"
                  className="form-input"
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setEditingDoc(null)}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleSaveMetadata}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
