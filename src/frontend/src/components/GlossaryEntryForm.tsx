import { useState, useEffect } from 'react'
import apiClient from '../api/client'
import type { GlossaryEntry, GlossaryEntryCreate, GlossaryEntryUpdate } from '../types'

interface Props {
  entry?: GlossaryEntry | null
  onClose: () => void
}

export default function GlossaryEntryForm({ entry, onClose }: Props) {
  const [formData, setFormData] = useState({
    term: '',
    definition: '',
    language: 'en' as 'en' | 'de',
    source: 'internal',
    source_document: '',
    domain_tags: '',
    validation_status: 'pending' as 'pending' | 'validated' | 'rejected',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (entry) {
      setFormData({
        term: entry.term,
        definition: entry.definition,
        language: entry.language,
        source: entry.source,
        source_document: entry.source_document || '',
        domain_tags: entry.domain_tags?.join(', ') || '',
        validation_status: entry.validation_status,
      })
    }
  }, [entry])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const domainTags = formData.domain_tags
        .split(',')
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0)

      if (entry) {
        // Update existing entry
        const updateData: GlossaryEntryUpdate = {
          term: formData.term,
          definition: formData.definition,
          language: formData.language,
          source: formData.source,
          source_document: formData.source_document || undefined,
          domain_tags: domainTags.length > 0 ? domainTags : undefined,
          validation_status: formData.validation_status,
        }
        await apiClient.updateGlossaryEntry(entry.id, updateData)
      } else {
        // Create new entry
        const createData: GlossaryEntryCreate = {
          term: formData.term,
          definition: formData.definition,
          language: formData.language,
          source: formData.source,
          source_document: formData.source_document || undefined,
          domain_tags: domainTags.length > 0 ? domainTags : undefined,
        }
        await apiClient.createGlossaryEntry(createData)
      }

      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save entry')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{entry ? 'Edit Entry' : 'New Entry'}</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Term *</label>
            <input
              type="text"
              value={formData.term}
              onChange={(e) => setFormData({ ...formData, term: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>Definition *</label>
            <textarea
              value={formData.definition}
              onChange={(e) => setFormData({ ...formData, definition: e.target.value })}
              required
              rows={4}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Language *</label>
              <select
                value={formData.language}
                onChange={(e) =>
                  setFormData({ ...formData, language: e.target.value as 'en' | 'de' })
                }
              >
                <option value="en">English</option>
                <option value="de">German</option>
              </select>
            </div>

            <div className="form-group">
              <label>Source *</label>
              <select
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              >
                <option value="internal">Internal</option>
                <option value="NAMUR">NAMUR</option>
                <option value="DIN">DIN</option>
                <option value="ASME">ASME</option>
                <option value="IEC">IEC</option>
                <option value="IATE">IATE</option>
              </select>
            </div>
          </div>

          {entry && (
            <div className="form-group">
              <label>Validation Status</label>
              <select
                value={formData.validation_status}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    validation_status: e.target.value as any,
                  })
                }
              >
                <option value="pending">Pending</option>
                <option value="validated">Validated</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          )}

          <div className="form-group">
            <label>Source Document</label>
            <input
              type="text"
              value={formData.source_document}
              onChange={(e) =>
                setFormData({ ...formData, source_document: e.target.value })
              }
              placeholder="Optional"
            />
          </div>

          <div className="form-group">
            <label>Domain Tags</label>
            <input
              type="text"
              value={formData.domain_tags}
              onChange={(e) =>
                setFormData({ ...formData, domain_tags: e.target.value })
              }
              placeholder="automation, measurement (comma separated)"
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving...' : entry ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
