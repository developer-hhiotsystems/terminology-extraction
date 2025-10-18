import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { UploadedDocument, DocumentType, DocumentProcessRequest } from '../types'

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

  const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

  // Load documents and types
  useEffect(() => {
    fetchDocuments()
    fetchDocumentTypes()
  }, [])

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
    if (processingDocs.has(doc.id)) {
      toast.warning('This document is already being processed')
      return
    }

    setProcessingDocs(prev => new Set(prev).add(doc.id))

    try {
      const processRequest: DocumentProcessRequest = {
        extract_terms: true,
        auto_validate: false,
        language: 'en',
        source: 'internal'
      }

      const result = await apiClient.processDocument(doc.id, processRequest)

      toast.success(
        `Processed ${doc.filename}: ${result.terms_saved} terms extracted`,
        { autoClose: 5000 }
      )

      fetchDocuments() // Refresh list
    } catch (err: any) {
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

    toast.info(`Processing ${pendingDocs.length} documents...`)

    let successCount = 0
    let failCount = 0

    for (const doc of pendingDocs) {
      try {
        await handleProcess(doc)
        successCount++
      } catch {
        failCount++
      }
    }

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

  // === RENDER ===

  const formatDate = (dateString: string) => new Date(dateString).toLocaleString()
  const formatFileSize = (bytes: number) => (bytes / 1024 / 1024).toFixed(2) + ' MB'

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
                      <td>{doc.document_number || '-'}</td>
                      <td>{formatFileSize(doc.file_size)}</td>
                      <td>
                        <span className={`status-badge status-${doc.upload_status}`}>
                          {doc.upload_status}
                        </span>
                      </td>
                      <td>{doc.processing_metadata?.terms_saved || '-'}</td>
                      <td className="date-col">{formatDate(doc.uploaded_at)}</td>
                      <td className="actions-cell">
                        {doc.upload_status === 'pending' && (
                          <button
                            className="btn-process-small"
                            onClick={() => handleProcess(doc)}
                            disabled={processingDocs.has(doc.id)}
                            title="Process document"
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
