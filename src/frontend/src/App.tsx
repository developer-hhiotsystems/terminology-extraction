import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import GlossaryList from './components/GlossaryList'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('glossary')

  return (
    <Router>
      <div className="app">
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
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<GlossaryList />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/documents" element={<DocumentList />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>Glossary Extraction & Validation API v2.0.0</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
