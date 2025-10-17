import { getKeyboardShortcuts, getModifierKey } from '../hooks/useKeyboardShortcuts'
import '../styles/KeyboardShortcutsHelp.css'

interface KeyboardShortcutsHelpProps {
  onClose: () => void
}

export default function KeyboardShortcutsHelp({ onClose }: KeyboardShortcutsHelpProps) {
  const shortcuts = getKeyboardShortcuts()
  const modKey = getModifierKey()

  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    const category = shortcut.category || 'Other'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(shortcut)
    return acc
  }, {} as Record<string, typeof shortcuts>)

  const renderKey = (keyCombo: string) => {
    // Split by + to handle combinations
    const keys = keyCombo.split('+')
    return (
      <span className="key-combination">
        {keys.map((key, index) => (
          <span key={index}>
            <kbd className="key">{key}</kbd>
            {index < keys.length - 1 && <span className="key-separator">+</span>}
          </span>
        ))}
      </span>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content shortcuts-help" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Keyboard Shortcuts</h2>
          <button className="close-btn" onClick={onClose} title="Close (Esc)">
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="shortcuts-intro">
            <p>
              Use keyboard shortcuts to navigate and perform actions faster.
              Your platform uses <strong>{modKey}</strong> as the modifier key.
            </p>
          </div>

          <div className="shortcuts-list">
            {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
              <div key={category} className="shortcuts-category">
                <h3 className="category-title">{category}</h3>
                <div className="shortcuts-items">
                  {categoryShortcuts.map((shortcut, index) => (
                    <div key={index} className="shortcut-item">
                      <div className="shortcut-keys">{renderKey(shortcut.key)}</div>
                      <div className="shortcut-description">{shortcut.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="shortcuts-footer">
            <p className="hint-text">
              Press <kbd className="key">?</kbd> anytime to show this help
            </p>
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn-primary" onClick={onClose}>
            Got it!
          </button>
        </div>
      </div>
    </div>
  )
}
