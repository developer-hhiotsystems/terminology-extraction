import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import type { DocumentType } from '../types'
import StatsDashboard from './StatsDashboard'

export default function AdminPanel() {
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [confirmText, setConfirmText] = useState('')

  // DocumentType management state
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([])
  const [loadingTypes, setLoadingTypes] = useState(true)
  const [showTypeForm, setShowTypeForm] = useState(false)
  const [editingType, setEditingType] = useState<DocumentType | null>(null)
  const [typeFormData, setTypeFormData] = useState({
    code: '',
    label_en: '',
    label_de: '',
    description: ''
  })

  // Load document types
  const loadDocumentTypes = async () => {
    try {
      setLoadingTypes(true)
      const types = await apiClient.getDocumentTypes()
      setDocumentTypes(types)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to load document types')
    } finally {
      setLoadingTypes(false)
    }
  }

  useEffect(() => {
    loadDocumentTypes()
  }, [])

  // Open form for creating new type
  const handleAddType = () => {
    setEditingType(null)
    setTypeFormData({ code: '', label_en: '', label_de: '', description: '' })
    setShowTypeForm(true)
  }

  // Open form for editing existing type
  const handleEditType = (type: DocumentType) => {
    setEditingType(type)
    setTypeFormData({
      code: type.code,
      label_en: type.label_en,
      label_de: type.label_de,
      description: type.description || ''
    })
    setShowTypeForm(true)
  }

  // Save document type (create or update)
  const handleSaveType = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      if (editingType) {
        await apiClient.updateDocumentType(editingType.id, typeFormData)
        toast.success('Document type updated successfully')
      } else {
        await apiClient.createDocumentType(typeFormData)
        toast.success('Document type created successfully')
      }

      setShowTypeForm(false)
      loadDocumentTypes()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to save document type')
    }
  }

  // Delete document type
  const handleDeleteType = async (type: DocumentType) => {
    if (!window.confirm(`Delete document type "${type.label_en}"? This will fail if any documents use this type.`)) {
      return
    }

    try {
      await apiClient.deleteDocumentType(type.id)
      toast.success('Document type deleted successfully')
      loadDocumentTypes()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete document type')
    }
  }

  const handleResetDatabase = async () => {
    if (confirmText !== 'RESET') {
      toast.error('Please type RESET to confirm')
      return
    }

    try {
      setResetting(true)
      const result = await apiClient.resetDatabase()
      toast.success(result.message || 'Database reset successfully')
      setShowResetConfirm(false)
      setConfirmText('')

      // Refresh the page to reload stats
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to reset database'
      toast.error(errorMsg)
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className="admin-panel">
      {/* Statistics Dashboard Section */}
      <StatsDashboard />

      {/* Document Type Management Section */}
      <div className="document-types-section">
        <div className="admin-section-header">
          <h2>Document Types Management</h2>
          <p>Manage bilingual (EN/DE) document type classifications</p>
        </div>

        <div className="document-types-header">
          <button className="btn-primary" onClick={handleAddType}>
            + Add Document Type
          </button>
        </div>

        {loadingTypes ? (
          <div className="loading">Loading document types...</div>
        ) : (
          <div className="document-types-table">
            <table>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>English Label</th>
                  <th>German Label</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documentTypes.map((type) => (
                  <tr key={type.id}>
                    <td><code>{type.code}</code></td>
                    <td>{type.label_en}</td>
                    <td>{type.label_de}</td>
                    <td>{type.description || '-'}</td>
                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-edit"
                          onClick={() => handleEditType(type)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn-delete-small"
                          onClick={() => handleDeleteType(type)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Admin Actions Section */}
      <div className="admin-actions-section">
        <div className="admin-section-header">
          <h2>⚙️ Admin Actions</h2>
          <p>Manage database and system settings</p>
        </div>

        <div className="admin-cards-grid">
          {/* Database Reset Card */}
          <div className="admin-action-card danger-card">
            <div className="action-card-header">
              <div className="action-icon danger-icon">🗑️</div>
              <div>
                <h3>Reset Database</h3>
                <p>Delete all glossary entries and documents</p>
              </div>
            </div>
            <div className="action-card-content">
              <div className="warning-box">
                <span className="warning-icon">⚠️</span>
                <div>
                  <strong>Warning:</strong> This action cannot be undone.
                  All glossary entries, uploaded documents, and files will be permanently deleted.
                </div>
              </div>
              <button
                className="btn-danger"
                onClick={() => setShowResetConfirm(true)}
                disabled={resetting}
              >
                Reset Database
              </button>
            </div>
          </div>

          {/* Backup Card (Future Feature) */}
          <div className="admin-action-card info-card">
            <div className="action-card-header">
              <div className="action-icon info-icon">💾</div>
              <div>
                <h3>Backup Database</h3>
                <p>Create a backup of all data</p>
              </div>
            </div>
            <div className="action-card-content">
              <p className="feature-status">Coming soon - Feature in development</p>
              <button className="btn-secondary" disabled>
                Create Backup
              </button>
            </div>
          </div>

          {/* Export Logs Card (Future Feature) */}
          <div className="admin-action-card info-card">
            <div className="action-card-header">
              <div className="action-icon info-icon">📋</div>
              <div>
                <h3>Export System Logs</h3>
                <p>Download system activity logs</p>
              </div>
            </div>
            <div className="action-card-content">
              <p className="feature-status">Coming soon - Feature in development</p>
              <button className="btn-secondary" disabled>
                Export Logs
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Document Type Form Modal */}
      {showTypeForm && (
        <div className="modal-overlay" onClick={() => setShowTypeForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingType ? 'Edit Document Type' : 'Add Document Type'}</h2>
              <button className="modal-close" onClick={() => setShowTypeForm(false)}>
                ×
              </button>
            </div>
            <form onSubmit={handleSaveType}>
              <div className="modal-body">
                <div className="form-group">
                  <label htmlFor="code">Code *</label>
                  <input
                    id="code"
                    type="text"
                    value={typeFormData.code}
                    onChange={(e) => setTypeFormData({ ...typeFormData, code: e.target.value })}
                    placeholder="e.g., manual, specification"
                    required
                    disabled={!!editingType}
                  />
                  {editingType && (
                    <small className="form-hint">Code cannot be changed after creation</small>
                  )}
                </div>

                <div className="form-group">
                  <label htmlFor="label_en">English Label *</label>
                  <input
                    id="label_en"
                    type="text"
                    value={typeFormData.label_en}
                    onChange={(e) => setTypeFormData({ ...typeFormData, label_en: e.target.value })}
                    placeholder="e.g., Manual"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="label_de">German Label *</label>
                  <input
                    id="label_de"
                    type="text"
                    value={typeFormData.label_de}
                    onChange={(e) => setTypeFormData({ ...typeFormData, label_de: e.target.value })}
                    placeholder="e.g., Handbuch"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    value={typeFormData.description}
                    onChange={(e) => setTypeFormData({ ...typeFormData, description: e.target.value })}
                    placeholder="Optional description of this document type"
                    rows={3}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowTypeForm(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingType ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reset Confirmation Modal */}
      {showResetConfirm && (
        <div className="modal-overlay">
          <div className="modal-content modal-danger">
            <div className="modal-header">
              <h2>⚠️ Confirm Database Reset</h2>
              <button
                className="modal-close"
                onClick={() => {
                  setShowResetConfirm(false)
                  setConfirmText('')
                }}
                disabled={resetting}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="danger-warning-box">
                <span className="danger-icon-large">🚨</span>
                <div>
                  <h3>This action cannot be undone!</h3>
                  <p>All of the following will be permanently deleted:</p>
                  <ul>
                    <li>All glossary entries</li>
                    <li>All uploaded documents</li>
                    <li>All files from disk</li>
                    <li>All processing history</li>
                  </ul>
                </div>
              </div>

              <div className="confirm-input-section">
                <label htmlFor="confirmText">
                  Type <strong>RESET</strong> to confirm:
                </label>
                <input
                  id="confirmText"
                  type="text"
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                  placeholder="Type RESET here"
                  className="confirm-input"
                  disabled={resetting}
                  autoFocus
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowResetConfirm(false)
                  setConfirmText('')
                }}
                disabled={resetting}
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                onClick={handleResetDatabase}
                disabled={resetting || confirmText !== 'RESET'}
              >
                {resetting ? 'Resetting...' : 'Reset Database'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
