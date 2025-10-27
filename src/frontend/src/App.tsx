import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import GlossaryList from './components/GlossaryList'
import Documents from './components/Documents'
import DocumentDetail from './components/DocumentDetail'
import StatsDashboard from './components/StatsDashboard'
import AdminPanel from './components/AdminPanel'
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp'
import CommandPalette from './components/CommandPalette'
import ThemeToggle from './components/ThemeToggle'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { useTheme } from './hooks/useTheme'
// Phase A: FTS5 Search Integration
import SearchPage from './pages/SearchPage'
// Phase B: Enhanced UI/UX Components
import EnhancedGlossaryPage from './pages/EnhancedGlossaryPage'
// Phase C: Relationship Extraction & Graph Visualization
import RelationshipExplorer from './components/RelationshipExplorer'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('glossary')
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)
  const [showCommandPalette, setShowCommandPalette] = useState(false)
  const { isDark } = useTheme()

  // Global keyboard shortcuts
  useKeyboardShortcuts({
    onShowHelp: () => setShowShortcutsHelp(true),
    onCloseModal: () => {
      setShowShortcutsHelp(false)
      setShowCommandPalette(false)
    },
    onCommandPalette: () => setShowCommandPalette(true),
  })

  return (
    <Router>
      <div className="app">
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme={isDark ? 'dark' : 'light'}
        />
        <header className="app-header">
          <div className="header-content">
            <div>
              <h1>Glossary Management System</h1>
              <p>Terminology Extraction & Validation Platform</p>
            </div>
            <ThemeToggle />
          </div>
        </header>

        <nav className="app-nav">
          <Link
            to="/"
            className={activeTab === 'glossary' ? 'active' : ''}
            onClick={() => setActiveTab('glossary')}
          >
            Glossary
          </Link>
          <Link
            to="/search"
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            🔍 Search
          </Link>
          <Link
            to="/enhanced-glossary"
            className={activeTab === 'enhanced' ? 'active' : ''}
            onClick={() => setActiveTab('enhanced')}
          >
            ✨ Enhanced View
          </Link>
          <Link
            to="/relationships"
            className={activeTab === 'relationships' ? 'active' : ''}
            onClick={() => setActiveTab('relationships')}
          >
            🕸️ Relationships
          </Link>
          <Link
            to="/documents"
            className={activeTab === 'documents' ? 'active' : ''}
            onClick={() => setActiveTab('documents')}
          >
            Documents
          </Link>
          <Link
            to="/statistics"
            className={activeTab === 'statistics' ? 'active' : ''}
            onClick={() => setActiveTab('statistics')}
          >
            Statistics
          </Link>
          <Link
            to="/admin"
            className={activeTab === 'admin' ? 'active' : ''}
            onClick={() => setActiveTab('admin')}
          >
            Admin
          </Link>
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<GlossaryList />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/statistics" element={<StatsDashboard />} />
            <Route path="/admin" element={<AdminPanel />} />
            {/* Phase A: FTS5 Search */}
            <Route path="/search" element={<SearchPage />} />
            {/* Phase B: Enhanced Glossary View */}
            <Route path="/enhanced-glossary" element={<EnhancedGlossaryPage />} />
            {/* Phase C: Relationship Graph */}
            <Route path="/relationships" element={<RelationshipExplorer />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>Glossary Extraction & Validation API v2.0.0</p>
          <button
            className="shortcuts-help-btn"
            onClick={() => setShowShortcutsHelp(true)}
            title="Keyboard shortcuts (Press ?)"
          >
            Keyboard Shortcuts (?)
          </button>
        </footer>

        {showShortcutsHelp && (
          <KeyboardShortcutsHelp onClose={() => setShowShortcutsHelp(false)} />
        )}

        {showCommandPalette && (
          <CommandPalette onClose={() => setShowCommandPalette(false)} />
        )}
      </div>
    </Router>
  )
}

export default App
