import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { UploadedDocument, DocumentType, DocumentProcessRequest } from '../types'

interface LogEntry {
  id: string
  timestamp: Date
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
  documentId?: number
  documentName?: string
  details?: string
}

export default function Documents() {
  // Upload state
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Documents list state
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<UploadedDocument[]>([])
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([])
  const [loading, setLoading] = useState(true)

  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Bulk operations
  const [selectedDocs, setSelectedDocs] = useState<Set<number>>(new Set())
  const [bulkDeleting, setBulkDeleting] = useState(false)

  // Processing state
  const [processingDocs, setProcessingDocs] = useState<Set<number>>(new Set())

  // Section visibility
  const [showUploadSection, setShowUploadSection] = useState(false)

  // Log View state
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [showLogView, setShowLogView] = useState(false)
  const logViewRef = useRef<HTMLDivElement>(null)

  // Inline editing state
  const [editingDoc, setEditingDoc] = useState<number | null>(null)
  const [editValues, setEditValues] = useState<{
    document_number?: string
    document_type_id?: number
    document_link?: string
  }>({})

  const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

  // Auto-scroll log view to bottom when new logs are added
  useEffect(() => {
    if (logViewRef.current && showLogView) {
      logViewRef.current.scrollTop = logViewRef.current.scrollHeight
    }
  }, [logs, showLogView])

  // Load documents and types
  useEffect(() => {
    fetchDocuments()
    fetchDocumentTypes()
  }, [])

  // Helper function to add log entry
  const addLog = (
    level: LogEntry['level'],
    message: string,
    documentId?: number,
    documentName?: string,
    details?: string
  ) => {
    const entry: LogEntry = {
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      level,
      message,
      documentId,
      documentName,
      details
    }
    setLogs(prev => [...prev, entry])

    // Auto-show log view on errors
    if (level === 'error') {
      setShowLogView(true)
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  // Apply filters
  useEffect(() => {
    let filtered = [...documents]

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(doc =>
        doc.filename.toLowerCase().includes(query) ||
        doc.document_number?.toLowerCase().includes(query)
      )
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => doc.upload_status === filterStatus)
    }

    setFilteredDocuments(filtered)
  }, [searchQuery, filterStatus, documents])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getDocuments()
      setDocuments(data)
      setFilteredDocuments(data)
    } catch (err: any) {
      toast.error('Failed to load documents')
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

  // === UPLOAD FUNCTIONS ===

  const validateFile = (file: File): string | null => {
    if (file.type !== 'application/pdf') {
      return `${file.name}: Invalid file type. Only PDF files are supported.`
    }
    if (file.size > MAX_FILE_SIZE) {
      return `${file.name}: File too large (max 50MB)`
    }
    if (file.size === 0) {
      return `${file.name}: Empty file`
    }
    return null
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files)
      addFiles(droppedFiles)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files)
      addFiles(selectedFiles)
    }
  }

  const addFiles = (newFiles: File[]) => {
    const validFiles: File[] = []
    const errors: string[] = []

    for (const file of newFiles) {
      const error = validateFile(file)
      if (error) {
        errors.push(error)
      } else {
        validFiles.push(file)
      }
    }

    if (errors.length > 0) {
      errors.forEach(err => toast.error(err))
    }

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles])
      toast.success(`Added ${validFiles.length} file(s)`)
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    setUploading(true)
    setUploadProgress(0)

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const results = await apiClient.uploadDocumentsBatch(files)

      clearInterval(progressInterval)
      setUploadProgress(100)

      toast.success(`Uploaded ${results.successful} of ${results.total_files} file(s)`)

      if (results.successful === results.total_files) {
        setFiles([])
        setShowUploadSection(false)
      }

      // Show errors if any
      if (results.failed > 0) {
        results.results
          .filter((r: any) => !r.success)
          .forEach((r: any) => toast.error(`${r.filename}: ${r.error}`))
      }

      // Refresh document list
      fetchDocuments()
    } catch (err: any) {
      toast.error('Failed to upload files')
    } finally {
      setUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  // === PROCESS FUNCTIONS ===

  const handleProcess = async (doc: UploadedDocument) => {
    // Validation: Check if document type is set
    if (!doc.document_type_id) {
      toast.error('Please set a Document Type before processing')
      addLog('error', `Processing blocked: Document type not set`, doc.id, doc.filename,
        `You must select a document type before processing. Click the "Type" column to edit.`)
      return
    }

    if (processingDocs.has(doc.id)) {
      toast.warning('This document is already being processed')
      addLog('warning', `Already processing`, doc.id, doc.filename)
      return
    }

    setProcessingDocs(prev => new Set(prev).add(doc.id))
    addLog('info', `Starting document processing...`, doc.id, doc.filename)

    try {
      const processRequest: DocumentProcessRequest = {
        extract_terms: true,
        auto_validate: false,
        language: 'en',
        source: 'internal'
      }

      addLog('info', `Sending process request to backend`, doc.id, doc.filename,
        `Parameters: extract_terms=true, language=en, source=internal`)

      const result = await apiClient.processDocument(doc.id, processRequest)

      addLog('success', `Successfully processed document`, doc.id, doc.filename,
        `Terms extracted: ${result.terms_saved}, Processing time: ${result.processing_time || 'N/A'}s`)

      toast.success(
        `Processed ${doc.filename}: ${result.terms_saved} terms extracted`,
        { autoClose: 5000 }
      )

      fetchDocuments() // Refresh list
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Unknown error'
      const errorDetails = err.response?.data ? JSON.stringify(err.response.data, null, 2) : err.stack

      addLog('error', `Processing failed`, doc.id, doc.filename,
        `Error: ${errorMessage}\n\nDetails:\n${errorDetails}`)

      toast.error(
        err.response?.data?.detail || `Failed to process ${doc.filename}`
      )
    } finally {
      setProcessingDocs(prev => {
        const newSet = new Set(prev)
        newSet.delete(doc.id)
        return newSet
      })
    }
  }

  // === BULK OPERATIONS ===

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

  const handleBulkDelete = async () => {
    if (selectedDocs.size === 0) {
      toast.warning('No documents selected')
      return
    }

    if (!confirm(`Delete ${selectedDocs.size} document(s)? This cannot be undone.`)) {
      return
    }

    setBulkDeleting(true)
    try {
      const deletePromises = Array.from(selectedDocs).map(id =>
        apiClient.deleteDocument(id)
      )
      await Promise.all(deletePromises)

      toast.success(`Deleted ${selectedDocs.size} document(s)`)
      setSelectedDocs(new Set())
      fetchDocuments()
    } catch (err: any) {
      toast.error('Failed to delete some documents')
    } finally {
      setBulkDeleting(false)
    }
  }

  const handleBulkProcess = async () => {
    if (selectedDocs.size === 0) {
      toast.warning('No documents selected')
      return
    }

    const docsToProcess = documents.filter(d => selectedDocs.has(d.id))
    const pendingDocs = docsToProcess.filter(d => d.upload_status === 'pending')

    if (pendingDocs.length === 0) {
      toast.warning('Selected documents are already processed or processing')
      return
    }

    if (!confirm(`Process ${pendingDocs.length} document(s)? This may take several minutes.`)) {
      return
    }

    setShowLogView(true) // Auto-show log view for bulk operations
    addLog('info', `Starting bulk processing`, undefined, undefined,
      `Processing ${pendingDocs.length} documents: ${pendingDocs.map(d => d.filename).join(', ')}`)

    toast.info(`Processing ${pendingDocs.length} documents...`)

    let successCount = 0
    let failCount = 0

    for (let i = 0; i < pendingDocs.length; i++) {
      const doc = pendingDocs[i]
      addLog('info', `Processing document ${i + 1}/${pendingDocs.length}`, doc.id, doc.filename)

      try {
        await handleProcess(doc)
        successCount++
      } catch (err) {
        failCount++
        addLog('error', `Document ${i + 1}/${pendingDocs.length} failed`, doc.id, doc.filename)
      }
    }

    addLog(failCount === 0 ? 'success' : 'warning',
      `Bulk processing completed`, undefined, undefined,
      `Success: ${successCount}, Failed: ${failCount}`)

    toast.success(
      `Processed ${successCount} documents. ${failCount > 0 ? `${failCount} failed.` : ''}`,
      { autoClose: 7000 }
    )

    setSelectedDocs(new Set())
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this document?')) return

    try {
      await apiClient.deleteDocument(id)
      toast.success('Document deleted')
      fetchDocuments()
      setSelectedDocs(prev => {
        const newSet = new Set(prev)
        newSet.delete(id)
        return newSet
      })
    } catch (err: any) {
      toast.error('Failed to delete document')
    }
  }

  // === INLINE EDITING ===

  const startEditing = (doc: UploadedDocument) => {
    setEditingDoc(doc.id)
    setEditValues({
      document_number: doc.document_number || '',
      document_type_id: doc.document_type_id,
      document_link: doc.document_link || ''
    })
  }

  const cancelEditing = () => {
    setEditingDoc(null)
    setEditValues({})
  }

  const saveEditing = async (docId: number) => {
    try {
      await apiClient.updateDocument(docId, editValues)
      toast.success('Document updated successfully')
      addLog('success', `Document metadata updated`, docId, undefined,
        `Doc #: ${editValues.document_number || 'not set'}, Type ID: ${editValues.document_type_id || 'not set'}, Link: ${editValues.document_link || 'not set'}`)
      fetchDocuments()
      setEditingDoc(null)
      setEditValues({})
    } catch (err: any) {
      toast.error('Failed to update document')
      addLog('error', `Failed to update document metadata`, docId, undefined,
        err.response?.data?.detail || err.message)
    }
  }

  const getDocumentTypeName = (typeId?: number) => {
    if (!typeId) return '-'
    const type = documentTypes.find(t => t.id === typeId)
    return type ? type.label_en : `Type ${typeId}`
  }

  // === RENDER ===

  const formatDate = (dateString: string) => new Date(dateString).toLocaleString()
  const formatFileSize = (bytes: number) => (bytes / 1024 / 1024).toFixed(2) + ' MB'
  const formatLogTime = (date: Date) => {
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const seconds = date.getSeconds().toString().padStart(2, '0')
    const ms = date.getMilliseconds().toString().padStart(3, '0')
    return `${hours}:${minutes}:${seconds}.${ms}`
  }

  if (loading) return <div className="loading">Loading documents...</div>

  return (
    <div className="documents-page">
      {/* Header */}
      <div className="documents-header">
        <div>
          <h2>Document Management</h2>
          <p>Upload PDFs and manage your document library</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowUploadSection(!showUploadSection)}
        >
          {showUploadSection ? '- Hide Upload' : '+ Upload PDFs'}
        </button>
      </div>

      {/* Upload Section (Collapsible) */}
      {showUploadSection && (
        <div className="upload-section">
          <h3>Upload New Documents</h3>

          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            {files.length > 0 ? (
              <div className="file-info">
                <p className="file-name">{files.length} file(s) selected</p>
                <p className="file-size">
                  Total: {(files.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="drop-zone-content">
                <p className="drop-zone-title">Drag & drop PDFs here</p>
                <p className="drop-zone-subtitle">or click to browse (multiple files supported)</p>
                <p className="drop-zone-limit">Max 50MB per file, up to 20 files at once</p>
              </div>
            )}
          </div>

          {files.length > 0 && (
            <>
              <div className="selected-files-list">
                <h4>Selected Files ({files.length})</h4>
                {files.map((file, index) => (
                  <div key={index} className="file-item">
                    <div className="file-item-info">
                      <span className="file-item-name">{file.name}</span>
                      <span className="file-item-size">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                    <button
                      className="btn-remove"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeFile(index)
                      }}
                      disabled={uploading}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>

              {uploading && uploadProgress > 0 && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
                  </div>
                  <p className="progress-text">{uploadProgress}% uploaded</p>
                </div>
              )}

              <div className="upload-actions">
                <button
                  className="btn-secondary"
                  onClick={() => setFiles([])}
                  disabled={uploading}
                >
                  Clear All
                </button>
                <button
                  className="btn-primary"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Log View Section */}
      {logs.length > 0 && (
        <div className="log-view-container">
          <div className="log-view-header">
            <div className="log-view-title">
              <span className="log-icon">📋</span>
              <h3>Processing Log</h3>
              <span className="log-count">{logs.length} entries</span>
            </div>
            <div className="log-view-actions">
              <button
                className="btn-secondary-small"
                onClick={clearLogs}
                title="Clear all logs"
              >
                Clear Logs
              </button>
              <button
                className="btn-secondary-small"
                onClick={() => setShowLogView(!showLogView)}
                title={showLogView ? "Collapse log view" : "Expand log view"}
              >
                {showLogView ? '▼ Collapse' : '▶ Expand'}
              </button>
            </div>
          </div>

          {showLogView && (
            <div className="log-view-content" ref={logViewRef}>
              {logs.map(log => (
                <div key={log.id} className={`log-entry log-${log.level}`}>
                  <div className="log-entry-header">
                    <span className="log-timestamp">{formatLogTime(log.timestamp)}</span>
                    <span className={`log-level log-level-${log.level}`}>
                      {log.level.toUpperCase()}
                    </span>
                    {log.documentName && (
                      <span className="log-document">
                        📄 {log.documentName}
                        {log.documentId && <span className="log-doc-id"> (ID: {log.documentId})</span>}
                      </span>
                    )}
                  </div>
                  <div className="log-message">{log.message}</div>
                  {log.details && (
                    <details className="log-details">
                      <summary>Show details</summary>
                      <pre className="log-details-content">{log.details}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Document List Section */}
      <div className="documents-list-section">
        {documents.length === 0 ? (
          <div className="empty-state">
            <p>No documents uploaded yet.</p>
            <p>Click "+ Upload PDFs" to get started.</p>
          </div>
        ) : (
          <>
            {/* Filters */}
            <div className="filter-bar">
              <input
                type="text"
                placeholder="Search by filename or document number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />

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

              {(searchQuery || filterStatus !== 'all') && (
                <button
                  onClick={() => {
                    setSearchQuery('')
                    setFilterStatus('all')
                  }}
                  className="btn-secondary-small"
                >
                  Clear Filters
                </button>
              )}
            </div>

            {/* Bulk Actions */}
            {selectedDocs.size > 0 && (
              <div className="bulk-actions-bar">
                <span className="selected-count">
                  {selectedDocs.size} document(s) selected
                </span>
                <button
                  onClick={handleBulkProcess}
                  className="btn-primary-small"
                  disabled={bulkDeleting}
                >
                  Process Selected
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="btn-danger"
                  disabled={bulkDeleting}
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
                        title="Select all"
                      />
                    </th>
                    <th>Filename</th>
                    <th>Doc #</th>
                    <th>Type <span className="required-field">*</span></th>
                    <th>Link</th>
                    <th>Size</th>
                    <th>Status</th>
                    <th>Terms</th>
                    <th>Uploaded</th>
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
                      <td className="filename">
                        <Link to={`/documents/${doc.id}`} className="document-link">
                          {doc.filename}
                        </Link>
                      </td>
                      {/* Document Number - Editable */}
                      <td className="editable-cell" onClick={() => editingDoc !== doc.id && startEditing(doc)}>
                        {editingDoc === doc.id ? (
                          <input
                            type="text"
                            className="inline-edit-input"
                            value={editValues.document_number || ''}
                            onChange={(e) => setEditValues(prev => ({
                              ...prev,
                              document_number: e.target.value
                            }))}
                            placeholder="e.g., DOC-2024-001"
                            maxLength={100}
                          />
                        ) : (
                          <span className={doc.document_number ? 'has-value' : 'no-value'}>
                            {doc.document_number || '-'}
                            <span className="edit-hint">✎</span>
                          </span>
                        )}
                      </td>

                      {/* Document Type - Editable */}
                      <td className="editable-cell" onClick={() => editingDoc !== doc.id && startEditing(doc)}>
                        {editingDoc === doc.id ? (
                          <select
                            className="inline-edit-select"
                            value={editValues.document_type_id || ''}
                            onChange={(e) => setEditValues(prev => ({
                              ...prev,
                              document_type_id: e.target.value ? parseInt(e.target.value) : undefined
                            }))}
                            autoFocus
                          >
                            <option value="">-- Select Type --</option>
                            {documentTypes.map(type => (
                              <option key={type.id} value={type.id}>
                                {type.label_en}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span className={doc.document_type_id ? 'has-value' : 'no-value'}>
                            {getDocumentTypeName(doc.document_type_id)}
                            <span className="edit-hint">✎</span>
                          </span>
                        )}
                      </td>

                      {/* Document Link - Editable */}
                      <td className="editable-cell" onClick={() => editingDoc !== doc.id && startEditing(doc)}>
                        {editingDoc === doc.id ? (
                          <input
                            type="text"
                            className="inline-edit-input"
                            value={editValues.document_link || ''}
                            onChange={(e) => setEditValues(prev => ({
                              ...prev,
                              document_link: e.target.value
                            }))}
                            placeholder="http://... or \\\\server\\path"
                          />
                        ) : (
                          <span className={doc.document_link ? 'has-value' : 'no-value'}>
                            {doc.document_link ? (
                              <a
                                href={doc.document_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="doc-link"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {doc.document_link.length > 40
                                  ? `${doc.document_link.substring(0, 40)}...`
                                  : doc.document_link}
                              </a>
                            ) : (
                              <span>-<span className="edit-hint">✎</span></span>
                            )}
                          </span>
                        )}
                      </td>

                      <td>{formatFileSize(doc.file_size)}</td>
                      <td>
                        <span className={`status-badge status-${doc.upload_status}`}>
                          {doc.upload_status}
                        </span>
                      </td>
                      <td>{doc.processing_metadata?.terms_saved || '-'}</td>
                      <td className="date-col">{formatDate(doc.uploaded_at)}</td>
                      <td className="actions-cell">
                        {editingDoc === doc.id ? (
                          <>
                            <button
                              className="btn-save-small"
                              onClick={(e) => {
                                e.stopPropagation()
                                saveEditing(doc.id)
                              }}
                              title="Save changes"
                            >
                              ✓ Save
                            </button>
                            <button
                              className="btn-cancel-small"
                              onClick={(e) => {
                                e.stopPropagation()
                                cancelEditing()
                              }}
                              title="Cancel editing"
                            >
                              ✗ Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            {doc.upload_status === 'pending' && (
                              <button
                                className="btn-process-small"
                                onClick={() => handleProcess(doc)}
                                disabled={processingDocs.has(doc.id)}
                                title={!doc.document_type_id ? "Set document type first" : "Process document"}
                              >
                                {processingDocs.has(doc.id) ? '⏳' : '▶️ Process'}
                              </button>
                            )}
                            <Link
                              to={`/documents/${doc.id}`}
                              className="btn-view-small"
                              title="View details"
                            >
                              View
                            </Link>
                            <button
                              className="btn-delete-small"
                              onClick={() => handleDelete(doc.id)}
                              title="Delete document"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
