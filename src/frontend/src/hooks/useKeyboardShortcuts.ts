import { useEffect, useCallback } from 'react'

export interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  metaKey?: boolean
  shiftKey?: boolean
  description: string
  action: () => void
  category?: string
}

interface UseKeyboardShortcutsOptions {
  onAddEntry?: () => void
  onFocusSearch?: () => void
  onCloseModal?: () => void
  onShowHelp?: () => void
  onCommandPalette?: () => void
}

/**
 * Custom hook for managing global keyboard shortcuts
 * Handles Ctrl/Cmd key detection for cross-platform compatibility
 */
export function useKeyboardShortcuts(options: UseKeyboardShortcutsOptions) {
  const {
    onAddEntry,
    onFocusSearch,
    onCloseModal,
    onShowHelp,
    onCommandPalette,
  } = options

  const isInputElement = useCallback((element: EventTarget | null): boolean => {
    if (!element || !(element instanceof HTMLElement)) return false
    const tagName = element.tagName.toLowerCase()
    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      element.isContentEditable
    )
  }, [])

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const { key, ctrlKey, metaKey, shiftKey, target } = event
      const isModifierPressed = ctrlKey || metaKey

      // Escape key - Close modals (works everywhere)
      if (key === 'Escape' && onCloseModal) {
        onCloseModal()
        return
      }

      // Help shortcut (?) - works when not in input
      if (key === '?' && !isInputElement(target) && onShowHelp) {
        event.preventDefault()
        onShowHelp()
        return
      }

      // Search shortcut (/) - focus search input when not already in an input
      if (key === '/' && !isInputElement(target) && onFocusSearch) {
        event.preventDefault()
        onFocusSearch()
        return
      }

      // Ctrl+N / Cmd+N - Add new entry
      if (
        key.toLowerCase() === 'n' &&
        isModifierPressed &&
        !shiftKey &&
        onAddEntry
      ) {
        event.preventDefault()
        onAddEntry()
        return
      }

      // Ctrl+K / Cmd+K - Command palette (future enhancement)
      if (
        key.toLowerCase() === 'k' &&
        isModifierPressed &&
        !shiftKey &&
        onCommandPalette
      ) {
        event.preventDefault()
        onCommandPalette()
        return
      }
    },
    [
      onAddEntry,
      onFocusSearch,
      onCloseModal,
      onShowHelp,
      onCommandPalette,
      isInputElement,
    ]
  )

  useEffect(() => {
    // Add event listener
    document.addEventListener('keydown', handleKeyDown)

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])
}

/**
 * Get the modifier key text based on the platform
 */
export function getModifierKey(): string {
  const isMac =
    typeof navigator !== 'undefined' &&
    /Mac|iPhone|iPod|iPad/i.test(navigator.platform)
  return isMac ? 'Cmd' : 'Ctrl'
}

/**
 * Get all available keyboard shortcuts
 */
export function getKeyboardShortcuts(): KeyboardShortcut[] {
  const modKey = getModifierKey()

  return [
    {
      key: `${modKey}+N`,
      description: 'Add new glossary entry',
      action: () => {},
      category: 'Actions',
    },
    {
      key: '/',
      description: 'Focus search input',
      action: () => {},
      category: 'Navigation',
    },
    {
      key: 'Escape',
      description: 'Close modal or form',
      action: () => {},
      category: 'Navigation',
    },
    {
      key: `${modKey}+K`,
      description: 'Open command palette (coming soon)',
      action: () => {},
      category: 'Navigation',
    },
    {
      key: '?',
      description: 'Show keyboard shortcuts',
      action: () => {},
      category: 'Help',
    },
  ]
}
