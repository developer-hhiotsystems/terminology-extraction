import { useState, useRef, useEffect } from 'react'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { UploadedDocument, DocumentProcessRequest, DocumentType } from '../types'

interface ErrorDetails {
  title: string
  message: string
  details?: string[]
  suggestion?: string
  canRetry: boolean
}

export default function DocumentUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [uploadedDoc, setUploadedDoc] = useState<UploadedDocument | null>(null)
  const [processResult, setProcessResult] = useState<any>(null)
  const [batchUploadResults, setBatchUploadResults] = useState<any>(null)
  const [error, setError] = useState<ErrorDetails | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Document metadata state
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([])
  const [loadingTypes, setLoadingTypes] = useState(false)
  const [documentMetadata, setDocumentMetadata] = useState({
    document_number: '',
    document_type_id: null as number | null,
    document_link: ''
  })

  const [processOptions, setProcessOptions] = useState<DocumentProcessRequest>({
    extract_terms: true,
    auto_validate: false,
    language: 'en',
    source: 'internal',
  })

  const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

  // Load document types on component mount
  useEffect(() => {
    const loadDocumentTypes = async () => {
      try {
        setLoadingTypes(true)
        const types = await apiClient.getDocumentTypes()
        setDocumentTypes(types)
      } catch (err: any) {
        console.error('Failed to load document types:', err)
        toast.error('Failed to load document types')
      } finally {
        setLoadingTypes(false)
      }
    }
    loadDocumentTypes()
  }, [])

  const parseError = (err: any, context: 'upload' | 'process'): ErrorDetails => {
    const errorMsg = err.response?.data?.detail || err.message || 'Unknown error'

    // File size error
    if (errorMsg.includes('file size') || errorMsg.includes('too large')) {
      return {
        title: 'File Too Large',
        message: 'The selected file exceeds the maximum allowed size.',
        details: ['Maximum file size: 50MB', `Your file: ${(file!.size / 1024 / 1024).toFixed(2)}MB`],
        suggestion: 'Try compressing the PDF or splitting it into smaller files.',
        canRetry: false
      }
    }

    // PDF parsing error
    if (errorMsg.includes('parse') || errorMsg.includes('corrupt') || errorMsg.includes('invalid PDF')) {
      return {
        title: 'Invalid PDF File',
        message: 'The file appears to be corrupted or is not a valid PDF.',
        details: [errorMsg],
        suggestion: 'Try re-saving the PDF or using a different file.',
        canRetry: false
      }
    }

    // Network/connection error
    if (errorMsg.includes('Network') || errorMsg.includes('timeout') || err.code === 'ERR_NETWORK') {
      return {
        title: 'Connection Error',
        message: 'Unable to connect to the server.',
        details: ['Check your internet connection', 'The server might be unavailable'],
        suggestion: 'Please try again in a moment.',
        canRetry: true
      }
    }

    // NLP/extraction error
    if (errorMsg.includes('extraction') || errorMsg.includes('NLP')) {
      return {
        title: 'Term Extraction Failed',
        message: 'The system encountered an error while extracting terms from the document.',
        details: [errorMsg],
        suggestion: 'The document might not contain extractable terminology. Try manual entry instead.',
        canRetry: true
      }
    }

    // Permission/auth error
    if (err.response?.status === 403 || err.response?.status === 401) {
      return {
        title: 'Permission Denied',
        message: 'You do not have permission to perform this action.',
        details: [errorMsg],
        suggestion: 'Contact your administrator if you believe this is an error.',
        canRetry: false
      }
    }

    // Server error
    if (err.response?.status >= 500) {
      return {
        title: 'Server Error',
        message: 'The server encountered an error while processing your request.',
        details: [errorMsg],
        suggestion: 'Please try again later. If the problem persists, contact support.',
        canRetry: true
      }
    }

    // Generic error
    return {
      title: context === 'upload' ? 'Upload Failed' : 'Processing Failed',
      message: errorMsg,
      details: [],
      suggestion: 'Please try again or contact support if the problem persists.',
      canRetry: true
    }
  }

  const validateFile = (selectedFile: File): ErrorDetails | null => {
    if (selectedFile.type !== 'application/pdf') {
      return {
        title: 'Invalid File Type',
        message: 'Only PDF files are supported.',
        details: [`Selected file type: ${selectedFile.type || 'unknown'}`],
        suggestion: 'Please select a PDF (.pdf) file.',
        canRetry: false
      }
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      return {
        title: 'File Too Large',
        message: `The file size exceeds the ${MAX_FILE_SIZE / 1024 / 1024}MB limit.`,
        details: [
          `Maximum size: ${MAX_FILE_SIZE / 1024 / 1024}MB`,
          `Your file: ${(selectedFile.size / 1024 / 1024).toFixed(2)}MB`
        ],
        suggestion: 'Try compressing the PDF or splitting it into smaller files.',
        canRetry: false
      }
    }

    if (selectedFile.size === 0) {
      return {
        title: 'Empty File',
        message: 'The selected file appears to be empty.',
        details: ['File size: 0 bytes'],
        suggestion: 'Please select a valid PDF file.',
        canRetry: false
      }
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
      const validFiles: File[] = []
      let hasError = false

      for (const file of droppedFiles) {
        const validationError = validateFile(file)
        if (validationError) {
          setError(validationError)
          hasError = true
          break
        } else {
          validFiles.push(file)
        }
      }

      if (!hasError) {
        setFiles(prev => [...prev, ...validFiles])
        setError(null)
        toast.success(`Added ${validFiles.length} file(s)`)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files)
      const validFiles: File[] = []
      let hasError = false

      for (const file of selectedFiles) {
        const validationError = validateFile(file)
        if (validationError) {
          setError(validationError)
          hasError = true
          break
        } else {
          validFiles.push(file)
        }
      }

      if (!hasError) {
        setFiles(prev => [...prev, ...validFiles])
        setError(null)
        toast.success(`Added ${validFiles.length} file(s)`)
      }
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    toast.info('File removed')
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    // Re-validate all files before upload
    for (const file of files) {
      const validationError = validateFile(file)
      if (validationError) {
        setError(validationError)
        return
      }
    }

    setUploading(true)
    setError(null)
    setProcessResult(null)
    setBatchUploadResults(null)
    setUploadProgress(0)

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const results = await apiClient.uploadDocumentsBatch(files)

      clearInterval(progressInterval)
      setUploadProgress(100)
      setBatchUploadResults(results)
      setError(null)

      toast.success(`Uploaded ${results.successful} of ${results.total_files} file(s) successfully`)

      // If all succeeded, clear the files list
      if (results.successful === results.total_files) {
        setFiles([])
      }
    } catch (err: any) {
      const errorDetails = parseError(err, 'upload')
      setError(errorDetails)
      toast.error(errorDetails.title)
    } finally {
      setUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const handleProcess = async () => {
    if (!uploadedDoc) return

    setProcessing(true)
    setError(null)

    try {
      // First, update document metadata if any fields are filled
      if (documentMetadata.document_number || documentMetadata.document_type_id || documentMetadata.document_link) {
        try {
          await apiClient.updateDocument(uploadedDoc.id, {
            document_number: documentMetadata.document_number || undefined,
            document_type_id: documentMetadata.document_type_id || undefined,
            document_link: documentMetadata.document_link || undefined,
          })
          toast.success('Document metadata updated')
        } catch (metaErr: any) {
          console.error('Failed to update metadata:', metaErr)
          toast.warning('Failed to save metadata, but continuing with processing...')
        }
      }

      // Then process the document
      const result = await apiClient.processDocument(uploadedDoc.id, processOptions)
      setProcessResult(result)
      setError(null)

      if (result.terms_saved > 0) {
        toast.success(`Successfully extracted ${result.terms_saved} terms from document`)
      } else {
        toast.warning('No terms were extracted. The document might not contain recognizable terminology.')
      }
    } catch (err: any) {
      const errorDetails = parseError(err, 'process')
      setError(errorDetails)
      toast.error(errorDetails.title)
    } finally {
      setProcessing(false)
    }
  }

  const handleRetry = () => {
    if (!error) return

    setError(null)

    if (uploadedDoc && !processResult) {
      // Retry processing
      handleProcess()
    } else if (files.length > 0 && !uploadedDoc) {
      // Retry upload
      handleUpload()
    }
  }

  const handleReset = () => {
    setFiles([])
    setUploadedDoc(null)
    setProcessResult(null)
    setBatchUploadResults(null)
    setError(null)
    setDocumentMetadata({
      document_number: '',
      document_type_id: null,
      document_link: ''
    })
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="document-upload">
      <h2>New Document</h2>
      <p>Upload a PDF document and configure metadata for automatic term extraction</p>

      {!uploadedDoc ? (
        <>
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
                <p className="drop-zone-title">Drag & drop your PDFs here</p>
                <p className="drop-zone-subtitle">or click to browse (multiple files supported)</p>
                <p className="drop-zone-limit">Maximum file size: 50MB per file, up to 20 files</p>
              </div>
            )}
          </div>

          {files.length > 0 && !error && (
            <>
              {/* File List */}
              <div className="selected-files-list">
                <h3>Selected Files ({files.length})</h3>
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
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>

              {uploading && uploadProgress > 0 && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="progress-text">{uploadProgress}% uploaded</p>
                </div>
              )}
              <div className="upload-actions">
                <button className="btn-secondary" onClick={handleReset} disabled={uploading}>
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

          {/* Batch Upload Results */}
          {batchUploadResults && (
            <div className="batch-upload-results">
              <h3>Upload Results</h3>
              <div className="results-summary">
                <p>Total: {batchUploadResults.total_files} |
                   Success: <span className="success-count">{batchUploadResults.successful}</span> |
                   Failed: <span className="failed-count">{batchUploadResults.failed}</span>
                </p>
              </div>
              <div className="results-list">
                {batchUploadResults.results.map((result: any, index: number) => (
                  <div key={index} className={`result-item ${result.success ? 'success' : 'error'}`}>
                    <span className="result-icon">{result.success ? '✓' : '✗'}</span>
                    <span className="result-filename">{result.filename}</span>
                    {result.error && <span className="result-error">{result.error}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="upload-success">
            <h3>✓ Upload Successful</h3>
            <p>File: {uploadedDoc.filename}</p>
            <p>Size: {(uploadedDoc.file_size / 1024 / 1024).toFixed(2)} MB</p>
            <p>Status: {uploadedDoc.upload_status}</p>
          </div>

          {!processResult && (
            <>
              {/* Document Metadata Section */}
              <div className="document-metadata-form">
                <h3>Document Information (Optional)</h3>
                <p className="form-hint">Add metadata to help organize and reference this document</p>

                <div className="option-group">
                  <label htmlFor="document_number">Document Number</label>
                  <input
                    id="document_number"
                    type="text"
                    value={documentMetadata.document_number}
                    onChange={(e) =>
                      setDocumentMetadata({
                        ...documentMetadata,
                        document_number: e.target.value,
                      })
                    }
                    placeholder="e.g., DOC-2024-001, SOP-123"
                    className="metadata-input"
                  />
                  <small className="field-hint">Unique identifier for this document</small>
                </div>

                <div className="option-group">
                  <label htmlFor="document_type">Document Type</label>
                  <select
                    id="document_type"
                    value={documentMetadata.document_type_id || ''}
                    onChange={(e) =>
                      setDocumentMetadata({
                        ...documentMetadata,
                        document_type_id: e.target.value ? Number(e.target.value) : null,
                      })
                    }
                    className="metadata-select"
                    disabled={loadingTypes}
                  >
                    <option value="">-- Select Type --</option>
                    {documentTypes.map((type) => (
                      <option key={type.id} value={type.id}>
                        {type.label_en} ({type.label_de})
                      </option>
                    ))}
                  </select>
                  <small className="field-hint">
                    Classification: Manual, Specification, Standard, etc.
                  </small>
                </div>

                <div className="option-group">
                  <label htmlFor="document_link">Document Link / Path</label>
                  <input
                    id="document_link"
                    type="text"
                    value={documentMetadata.document_link}
                    onChange={(e) =>
                      setDocumentMetadata({
                        ...documentMetadata,
                        document_link: e.target.value,
                      })
                    }
                    placeholder="https://... or \\server\path\file.pdf or /mnt/docs/file.pdf"
                    className="metadata-input"
                  />
                  <small className="field-hint">
                    URL, UNC path (\\server\share), or file system path
                  </small>
                </div>
              </div>

              <div className="process-options">
                <h3>Processing Options</h3>

                <div className="option-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={processOptions.extract_terms}
                      onChange={(e) =>
                        setProcessOptions({
                          ...processOptions,
                          extract_terms: e.target.checked,
                        })
                      }
                    />
                    Extract Terms (NLP)
                  </label>
                </div>

                <div className="option-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={processOptions.auto_validate}
                      onChange={(e) =>
                        setProcessOptions({
                          ...processOptions,
                          auto_validate: e.target.checked,
                        })
                      }
                    />
                    Auto-validate Terms
                  </label>
                </div>

                <div className="option-group">
                  <label>Language</label>
                  <select
                    value={processOptions.language}
                    onChange={(e) =>
                      setProcessOptions({
                        ...processOptions,
                        language: e.target.value as 'en' | 'de',
                      })
                    }
                  >
                    <option value="en">English</option>
                    <option value="de">German</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>Source</label>
                  <select
                    value={processOptions.source}
                    onChange={(e) =>
                      setProcessOptions({
                        ...processOptions,
                        source: e.target.value,
                      })
                    }
                  >
                    <option value="internal">Internal</option>
                    <option value="NAMUR">NAMUR</option>
                    <option value="DIN">DIN</option>
                    <option value="ASME">ASME</option>
                    <option value="IEC">IEC</option>
                  </select>
                </div>
              </div>

              <div className="process-actions">
                <button className="btn-secondary" onClick={handleReset}>
                  Upload Another
                </button>
                <button
                  className="btn-primary"
                  onClick={handleProcess}
                  disabled={processing}
                >
                  {processing ? 'Processing...' : 'Process Document'}
                </button>
              </div>
            </>
          )}

          {processResult && (
            <div className="process-result">
              <h3>✓ Processing Complete</h3>
              <div className="result-stats">
                <div className="stat">
                  <span className="stat-label">Text Extracted:</span>
                  <span className="stat-value">
                    {processResult.extracted_text_length.toLocaleString()} chars
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Terms Found:</span>
                  <span className="stat-value">{processResult.terms_extracted}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Terms Saved:</span>
                  <span className="stat-value">{processResult.terms_saved}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Processing Time:</span>
                  <span className="stat-value">
                    {processResult.processing_time_seconds}s
                  </span>
                </div>
              </div>

              {processResult.errors && processResult.errors.length > 0 && (
                <div className="process-errors">
                  <h4>Errors:</h4>
                  <ul>
                    {processResult.errors.map((err: string, idx: number) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="result-actions">
                <button className="btn-secondary" onClick={handleReset}>
                  Upload Another PDF
                </button>
                <button
                  className="btn-primary"
                  onClick={() => (window.location.href = '/')}
                >
                  View Glossary
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {error && (
        <div className="enhanced-error">
          <div className="error-header">
            <span className="error-icon">⚠️</span>
            <h3 className="error-title">{error.title}</h3>
          </div>
          <p className="error-message">{error.message}</p>

          {error.details && error.details.length > 0 && (
            <div className="error-details">
              <strong>Details:</strong>
              <ul>
                {error.details.map((detail, idx) => (
                  <li key={idx}>{detail}</li>
                ))}
              </ul>
            </div>
          )}

          {error.suggestion && (
            <div className="error-suggestion">
              <span className="suggestion-icon">💡</span>
              <p>{error.suggestion}</p>
            </div>
          )}

          <div className="error-actions">
            {error.canRetry && (
              <button className="btn-primary" onClick={handleRetry}>
                🔄 Retry
              </button>
            )}
            <button className="btn-secondary" onClick={handleReset}>
              Start Over
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
