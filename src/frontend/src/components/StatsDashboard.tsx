import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import apiClient from '../api/client'

interface AdminStats {
  total_glossary_entries: number
  total_documents: number
  entries_by_language: Record<string, number>
  entries_by_source: Record<string, number>
  entries_by_validation_status: Record<string, number>
  recent_activity: {
    last_entry_created: string | null
    last_document_uploaded: string | null
    entries_created_today: number
    documents_uploaded_today: number
  }
}

export default function StatsDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getDatabaseStats()
      setStats(data)
      setError(null)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load statistics'
      setError(errorMsg)
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A'
    try {
      return new Date(dateStr).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateStr
    }
  }

  const getStatusBadgeClass = (status: string): string => {
    const statusMap: Record<string, string> = {
      validated: 'status-validated',
      pending: 'status-pending',
      rejected: 'status-rejected'
    }
    return statusMap[status.toLowerCase()] || 'status-default'
  }

  const getLanguageName = (code: string): string => {
    const languages: Record<string, string> = {
      en: 'English',
      de: 'German',
      fr: 'French',
      es: 'Spanish',
      it: 'Italian'
    }
    return languages[code] || code.toUpperCase()
  }

  if (loading) {
    return (
      <div className="stats-dashboard">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading statistics...</p>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="stats-dashboard">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p>Error loading statistics</p>
          <button className="btn-primary" onClick={fetchStats}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  const totalEntriesByLang = Object.values(stats.entries_by_language).reduce((a, b) => a + b, 0)
  const totalEntriesBySource = Object.values(stats.entries_by_source).reduce((a, b) => a + b, 0)

  return (
    <div className="stats-dashboard">
      <div className="stats-header">
        <div>
          <h2>Statistics Dashboard</h2>
          <p>System-wide metrics and analytics</p>
        </div>
        <button className="btn-secondary" onClick={fetchStats}>
          🔄 Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="stats-grid">
        <div className="stat-card stat-primary">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <div className="stat-label">Total Entries</div>
            <div className="stat-value">{stats.total_glossary_entries.toLocaleString()}</div>
          </div>
        </div>

        <div className="stat-card stat-secondary">
          <div className="stat-icon">📄</div>
          <div className="stat-content">
            <div className="stat-label">Documents Uploaded</div>
            <div className="stat-value">{stats.total_documents.toLocaleString()}</div>
          </div>
        </div>

        <div className="stat-card stat-success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">Entries Today</div>
            <div className="stat-value">{stats.recent_activity.entries_created_today}</div>
          </div>
        </div>

        <div className="stat-card stat-info">
          <div className="stat-icon">📥</div>
          <div className="stat-content">
            <div className="stat-label">Uploads Today</div>
            <div className="stat-value">{stats.recent_activity.documents_uploaded_today}</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        {/* Entries by Language */}
        <div className="chart-card">
          <h3>Entries by Language</h3>
          <div className="chart-content">
            {Object.keys(stats.entries_by_language).length === 0 ? (
              <div className="empty-chart">No language data available</div>
            ) : (
              <div className="bar-chart">
                {Object.entries(stats.entries_by_language)
                  .sort(([, a], [, b]) => b - a)
                  .map(([lang, count]) => {
                    const percentage = totalEntriesByLang > 0
                      ? (count / totalEntriesByLang) * 100
                      : 0
                    return (
                      <div key={lang} className="bar-item">
                        <div className="bar-label">
                          <span className="bar-name">{getLanguageName(lang)}</span>
                          <span className="bar-count">{count}</span>
                        </div>
                        <div className="bar-track">
                          <div
                            className="bar-fill bar-fill-language"
                            style={{ width: `${percentage}%` }}
                          >
                            <span className="bar-percentage">{percentage.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
          </div>
        </div>

        {/* Entries by Source */}
        <div className="chart-card">
          <h3>Entries by Source</h3>
          <div className="chart-content">
            {Object.keys(stats.entries_by_source).length === 0 ? (
              <div className="empty-chart">No source data available</div>
            ) : (
              <div className="bar-chart">
                {Object.entries(stats.entries_by_source)
                  .sort(([, a], [, b]) => b - a)
                  .map(([source, count]) => {
                    const percentage = totalEntriesBySource > 0
                      ? (count / totalEntriesBySource) * 100
                      : 0
                    return (
                      <div key={source} className="bar-item">
                        <div className="bar-label">
                          <span className="bar-name">{source}</span>
                          <span className="bar-count">{count}</span>
                        </div>
                        <div className="bar-track">
                          <div
                            className="bar-fill bar-fill-source"
                            style={{ width: `${percentage}%` }}
                          >
                            <span className="bar-percentage">{percentage.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Validation Status */}
      <div className="status-section">
        <h3>Validation Status Distribution</h3>
        <div className="status-badges">
          {Object.keys(stats.entries_by_validation_status).length === 0 ? (
            <div className="empty-state-small">No validation data available</div>
          ) : (
            Object.entries(stats.entries_by_validation_status).map(([status, count]) => (
              <div key={status} className={`status-badge-item ${getStatusBadgeClass(status)}`}>
                <span className="status-name">{status}</span>
                <span className="status-count">{count}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <h3>Recent Activity</h3>
        <div className="activity-grid">
          <div className="activity-item">
            <div className="activity-icon">🕒</div>
            <div className="activity-content">
              <div className="activity-label">Last Entry Created</div>
              <div className="activity-value">
                {formatDate(stats.recent_activity.last_entry_created)}
              </div>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">📤</div>
            <div className="activity-content">
              <div className="activity-label">Last Document Uploaded</div>
              <div className="activity-value">
                {formatDate(stats.recent_activity.last_document_uploaded)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
