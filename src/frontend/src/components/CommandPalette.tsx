import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'

interface Command {
  id: string
  label: string
  description: string
  category: string
  icon: string
  action: () => void
  keywords?: string[]
}

interface CommandPaletteProps {
  onClose: () => void
  onAddEntry?: () => void
  onExportCSV?: () => void
  onExportExcel?: () => void
  onExportJSON?: () => void
  onRefreshData?: () => void
}

export default function CommandPalette({
  onClose,
  onAddEntry,
  onExportCSV,
  onExportExcel,
  onExportJSON,
  onRefreshData,
}: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)

  const commands: Command[] = [
    // Navigation
    {
      id: 'nav-glossary',
      label: 'Go to Glossary',
      description: 'View all glossary entries',
      category: 'Navigation',
      icon: '📚',
      action: () => { navigate('/'); onClose(); },
      keywords: ['glossary', 'entries', 'terms', 'home'],
    },
    {
      id: 'nav-upload',
      label: 'Go to Upload PDF',
      description: 'Upload and process PDF documents',
      category: 'Navigation',
      icon: '📤',
      action: () => { navigate('/upload'); onClose(); },
      keywords: ['upload', 'pdf', 'document', 'import'],
    },
    {
      id: 'nav-documents',
      label: 'Go to Documents',
      description: 'View uploaded documents',
      category: 'Navigation',
      icon: '📄',
      action: () => { navigate('/documents'); onClose(); },
      keywords: ['documents', 'files', 'uploads'],
    },
    {
      id: 'nav-statistics',
      label: 'Go to Statistics',
      description: 'View system statistics and metrics',
      category: 'Navigation',
      icon: '📊',
      action: () => { navigate('/statistics'); onClose(); },
      keywords: ['statistics', 'stats', 'metrics', 'dashboard'],
    },
    {
      id: 'nav-admin',
      label: 'Go to Admin Panel',
      description: 'Access admin tools and database management',
      category: 'Navigation',
      icon: '⚙️',
      action: () => { navigate('/admin'); onClose(); },
      keywords: ['admin', 'settings', 'management'],
    },
    // Actions
    {
      id: 'action-add-entry',
      label: 'Add New Entry',
      description: 'Create a new glossary entry',
      category: 'Actions',
      icon: '➕',
      action: () => { onAddEntry?.(); onClose(); },
      keywords: ['add', 'new', 'create', 'entry', 'term'],
    },
    {
      id: 'action-refresh',
      label: 'Refresh Data',
      description: 'Reload current data',
      category: 'Actions',
      icon: '🔄',
      action: () => { onRefreshData?.(); onClose(); toast.info('Data refreshed'); },
      keywords: ['refresh', 'reload', 'update'],
    },
    // Export
    {
      id: 'export-csv',
      label: 'Export to CSV',
      description: 'Download glossary as CSV file',
      category: 'Export',
      icon: '📥',
      action: () => { onExportCSV?.(); onClose(); },
      keywords: ['export', 'download', 'csv', 'spreadsheet'],
    },
    {
      id: 'export-excel',
      label: 'Export to Excel',
      description: 'Download glossary as Excel file',
      category: 'Export',
      icon: '📗',
      action: () => { onExportExcel?.(); onClose(); },
      keywords: ['export', 'download', 'excel', 'xlsx', 'spreadsheet'],
    },
    {
      id: 'export-json',
      label: 'Export to JSON',
      description: 'Download glossary as JSON file',
      category: 'Export',
      icon: '📋',
      action: () => { onExportJSON?.(); onClose(); },
      keywords: ['export', 'download', 'json', 'data'],
    },
    // Help
    {
      id: 'help-shortcuts',
      label: 'View Keyboard Shortcuts',
      description: 'Show all available keyboard shortcuts',
      category: 'Help',
      icon: '⌨️',
      action: () => { onClose(); toast.info('Press ? to see keyboard shortcuts'); },
      keywords: ['help', 'shortcuts', 'keys', 'keyboard'],
    },
  ]

  const filteredCommands = commands.filter((cmd) => {
    if (!query) return true
    const searchStr = query.toLowerCase()
    return (
      cmd.label.toLowerCase().includes(searchStr) ||
      cmd.description.toLowerCase().includes(searchStr) ||
      cmd.category.toLowerCase().includes(searchStr) ||
      cmd.keywords?.some((keyword) => keyword.includes(searchStr))
    )
  })

  const groupedCommands: Record<string, Command[]> = {}
  filteredCommands.forEach((cmd) => {
    if (!groupedCommands[cmd.category]) {
      groupedCommands[cmd.category] = []
    }
    groupedCommands[cmd.category].push(cmd)
  })

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) =>
        prev < filteredCommands.length - 1 ? prev + 1 : prev
      )
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action()
      }
    } else if (e.key === 'Escape') {
      onClose()
    }
  }

  return (
    <div className="modal-overlay command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        <div className="command-palette-header">
          <span className="command-palette-icon">⚡</span>
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="command-palette-input"
          />
          <button className="command-palette-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="command-palette-results">
          {filteredCommands.length === 0 ? (
            <div className="command-palette-empty">
              <span className="empty-icon">🔍</span>
              <p>No commands found</p>
              <p className="empty-hint">Try different keywords</p>
            </div>
          ) : (
            Object.entries(groupedCommands).map(([category, commands]) => (
              <div key={category} className="command-group">
                <div className="command-category">{category}</div>
                {commands.map((cmd) => {
                  const globalIndex = filteredCommands.indexOf(cmd)
                  return (
                    <button
                      key={cmd.id}
                      className={`command-item ${
                        globalIndex === selectedIndex ? 'selected' : ''
                      }`}
                      onClick={() => cmd.action()}
                      onMouseEnter={() => setSelectedIndex(globalIndex)}
                    >
                      <span className="command-icon">{cmd.icon}</span>
                      <div className="command-content">
                        <div className="command-label">{cmd.label}</div>
                        <div className="command-description">{cmd.description}</div>
                      </div>
                    </button>
                  )
                })}
              </div>
            ))
          )}
        </div>

        <div className="command-palette-footer">
          <div className="command-palette-hints">
            <span className="hint">
              <kbd>↑</kbd> <kbd>↓</kbd> Navigate
            </span>
            <span className="hint">
              <kbd>Enter</kbd> Select
            </span>
            <span className="hint">
              <kbd>Esc</kbd> Close
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
