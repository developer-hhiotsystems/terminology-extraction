import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { UploadedDocument, GlossaryEntry } from '../types'

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<UploadedDocument | null>(null)
  const [relatedTerms, setRelatedTerms] = useState<GlossaryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pdfViewerType, setPdfViewerType] = useState<'iframe' | 'fallback'>('iframe')

  useEffect(() => {
    if (!id) return

    const fetchDocument = async () => {
      try {
        setLoading(true)
        const docId = parseInt(id, 10)

        // Fetch document details
        const docData = await apiClient.getDocument(docId)
        setDocument(docData)

        // Fetch terms that reference this document
        // We'll need to filter all glossary entries to find those from this document
        const allEntries = await apiClient.getGlossaryEntries({ limit: 1000 })
        const filtered = allEntries.filter(entry =>
          entry.source_document === docData.filename ||
          entry.definitions?.some(def => def.source_doc_id === docId)
        )
        setRelatedTerms(filtered)

        setError(null)
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to load document'
        setError(errorMsg)
        toast.error(errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [id])

  const handleDelete = async () => {
    if (!document || !window.confirm(`Delete document "${document.filename}"?`)) return

    try {
      await apiClient.deleteDocument(document.id)
      toast.success('Document deleted successfully')
      navigate('/documents')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  const renderDocumentLink = (link: string) => {
    // Detect link type and render appropriately
    if (link.startsWith('http://') || link.startsWith('https://')) {
      return (
        <a href={link} target="_blank" rel="noopener noreferrer" className="external-link">
          {link}
        </a>
      )
    } else if (link.startsWith('file://') || link.startsWith('\\\\')) {
      return (
        <span className="unc-path" title="Local or network path">
          {link}
        </span>
      )
    } else {
      return <span>{link}</span>
    }
  }

  if (loading) return <div className="loading">Loading document details...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!document) return <div className="error">Document not found</div>

  return (
    <div className="document-detail">
      <div className="document-detail-header">
        <button onClick={() => navigate('/documents')} className="btn-back">
          ← Back to Documents
        </button>
        <h2>Document Details</h2>
        <button onClick={handleDelete} className="btn-danger">
          Delete Document
        </button>
      </div>

      <div className="document-detail-content">
        {/* Document Metadata Card */}
        <div className="document-metadata-card">
          <h3>Metadata</h3>
          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="metadata-label">Filename:</span>
              <span className="metadata-value">{document.filename}</span>
            </div>

            {document.document_number && (
              <div className="metadata-item">
                <span className="metadata-label">Document Number:</span>
                <span className="metadata-value">{document.document_number}</span>
              </div>
            )}

            <div className="metadata-item">
              <span className="metadata-label">File Size:</span>
              <span className="metadata-value">{formatFileSize(document.file_size)}</span>
            </div>

            <div className="metadata-item">
              <span className="metadata-label">Upload Status:</span>
              <span className={`status-badge status-${document.upload_status}`}>
                {document.upload_status}
              </span>
            </div>

            <div className="metadata-item">
              <span className="metadata-label">Uploaded At:</span>
              <span className="metadata-value">{formatDate(document.uploaded_at)}</span>
            </div>

            {document.processed_at && (
              <div className="metadata-item">
                <span className="metadata-label">Processed At:</span>
                <span className="metadata-value">{formatDate(document.processed_at)}</span>
              </div>
            )}

            {document.document_link && (
              <div className="metadata-item full-width">
                <span className="metadata-label">Document Link:</span>
                <span className="metadata-value">{renderDocumentLink(document.document_link)}</span>
              </div>
            )}

            {document.processing_metadata && (
              <>
                {document.processing_metadata.pages && (
                  <div className="metadata-item">
                    <span className="metadata-label">Pages:</span>
                    <span className="metadata-value">{document.processing_metadata.pages}</span>
                  </div>
                )}

                {document.processing_metadata.terms_extracted !== undefined && (
                  <div className="metadata-item">
                    <span className="metadata-label">Terms Extracted:</span>
                    <span className="metadata-value">{document.processing_metadata.terms_extracted}</span>
                  </div>
                )}

                {document.processing_metadata.terms_saved !== undefined && (
                  <div className="metadata-item">
                    <span className="metadata-label">Terms Saved:</span>
                    <span className="metadata-value">{document.processing_metadata.terms_saved}</span>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="pdf-viewer-container">
          <div className="pdf-viewer-header">
            <h3>PDF Preview</h3>
            <div className="viewer-controls">
              <button
                className={`btn-viewer-toggle ${pdfViewerType === 'iframe' ? 'active' : ''}`}
                onClick={() => setPdfViewerType('iframe')}
              >
                Embedded View
              </button>
              <a
                href={`http://localhost:9123${document.file_path.replace('./data', '/data')}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary"
              >
                Open in New Tab
              </a>
            </div>
          </div>

          {pdfViewerType === 'iframe' ? (
            <iframe
              src={`http://localhost:9123${document.file_path.replace('./data', '/data')}`}
              className="pdf-iframe"
              title={`PDF viewer for ${document.filename}`}
              onError={() => {
                toast.warning('Failed to load PDF preview. Try opening in a new tab.')
                setPdfViewerType('fallback')
              }}
            />
          ) : (
            <div className="pdf-fallback">
              <p>PDF preview unavailable in embedded view.</p>
              <a
                href={`http://localhost:9123${document.file_path.replace('./data', '/data')}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary"
              >
                Open PDF in New Tab
              </a>
            </div>
          )}
        </div>

        {/* Related Terms */}
        <div className="related-terms-card">
          <h3>Extracted Terms ({relatedTerms.length})</h3>
          {relatedTerms.length === 0 ? (
            <p className="empty-state">No terms extracted from this document yet.</p>
          ) : (
            <div className="terms-list">
              {relatedTerms.map(term => (
                <div key={term.id} className="term-item">
                  <div className="term-header">
                    <Link to="/" className="term-link">
                      <strong>{term.term}</strong>
                    </Link>
                    <div className="term-badges">
                      <span className={`badge lang-${term.language}`}>
                        {term.language.toUpperCase()}
                      </span>
                      <span className={`badge status-${term.validation_status}`}>
                        {term.validation_status}
                      </span>
                    </div>
                  </div>
                  {term.definitions && term.definitions.length > 0 && (
                    <p className="term-definition">
                      {term.definitions.find(d => d.is_primary)?.text || term.definitions[0]?.text}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
