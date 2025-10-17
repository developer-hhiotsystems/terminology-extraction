import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import GlossaryList from './components/GlossaryList'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'
import StatsDashboard from './components/StatsDashboard'
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('glossary')
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)

  // Global keyboard shortcuts
  useKeyboardShortcuts({
    onShowHelp: () => setShowShortcutsHelp(true),
    onCloseModal: () => setShowShortcutsHelp(false),
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
            to="/upload"
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload PDF
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
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<GlossaryList />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/documents" element={<DocumentList />} />
            <Route path="/statistics" element={<StatsDashboard />} />
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
      </div>
    </Router>
  )
}

export default App
