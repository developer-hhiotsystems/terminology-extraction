import { useState, useEffect } from 'react'
import apiClient from '../api/client'
import type { UploadedDocument } from '../types'

export default function DocumentList() {
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getDocuments()
      setDocuments(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await apiClient.deleteDocument(id)
      fetchDocuments()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

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
        <div className="documents-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Size</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Processed</th>
                <th>Terms Extracted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.id}</td>
                  <td className="filename">{doc.filename}</td>
                  <td>{formatFileSize(doc.file_size)}</td>
                  <td>
                    <span className={`status-badge status-${doc.upload_status}`}>
                      {doc.upload_status}
                    </span>
                  </td>
                  <td>{formatDate(doc.uploaded_at)}</td>
                  <td>
                    {doc.processed_at ? formatDate(doc.processed_at) : '-'}
                  </td>
                  <td>
                    {doc.processing_metadata?.terms_saved || '-'}
                  </td>
                  <td>
                    <button
                      className="btn-delete-small"
                      onClick={() => handleDelete(doc.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
