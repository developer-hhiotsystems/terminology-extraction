import { useState, useRef } from 'react'
import apiClient from '../api/client'
import type { UploadedDocument, DocumentProcessRequest } from '../types'

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [uploadedDoc, setUploadedDoc] = useState<UploadedDocument | null>(null)
  const [processResult, setProcessResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [processOptions, setProcessOptions] = useState<DocumentProcessRequest>({
    extract_terms: true,
    auto_validate: false,
    language: 'en',
    source: 'internal',
  })

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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile)
        setError(null)
      } else {
        setError('Please upload a PDF file')
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please select a PDF file')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setProcessResult(null)

    try {
      const doc = await apiClient.uploadDocument(file)
      setUploadedDoc(doc)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleProcess = async () => {
    if (!uploadedDoc) return

    setProcessing(true)
    setError(null)

    try {
      const result = await apiClient.processDocument(uploadedDoc.id, processOptions)
      setProcessResult(result)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Processing failed')
    } finally {
      setProcessing(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setUploadedDoc(null)
    setProcessResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="document-upload">
      <h2>Upload PDF Document</h2>
      <p>Upload a PDF to automatically extract technical terminology</p>

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
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            {file ? (
              <div className="file-info">
                <p className="file-name">{file.name}</p>
                <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <div className="drop-zone-content">
                <p className="drop-zone-title">Drag & drop your PDF here</p>
                <p className="drop-zone-subtitle">or click to browse</p>
                <p className="drop-zone-limit">Maximum file size: 50MB</p>
              </div>
            )}
          </div>

          {file && (
            <div className="upload-actions">
              <button className="btn-secondary" onClick={handleReset}>
                Clear
              </button>
              <button
                className="btn-primary"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload PDF'}
              </button>
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

      {error && <div className="error-message">{error}</div>}
    </div>
  )
}
