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
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('glossary')
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)
  const [showCommandPalette, setShowCommandPalette] = useState(false)

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
          theme="dark"
        />
        <header className="app-header">
          <h1>Glossary Management System</h1>
          <p>Terminology Extraction & Validation Platform</p>
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
