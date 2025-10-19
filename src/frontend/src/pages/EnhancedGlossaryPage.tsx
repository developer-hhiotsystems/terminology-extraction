import { useState, useEffect } from 'react';
import BilingualCard from '../components/BilingualCard';
import TermDetailView from '../components/TermDetailView';
import BulkOperations from '../components/BulkOperations';
import ExtractionProgress, { type ProcessingTask } from '../components/ExtractionProgress';
import apiClient from '../api/client';
import type { GlossaryEntry } from '../types';
import './EnhancedGlossaryPage.css';

/**
 * EnhancedGlossaryPage - Integration Example for Phase B Components
 *
 * Demonstrates all Phase B UI/UX improvements:
 * - BilingualCard for side-by-side term display
 * - TermDetailView for detailed term exploration
 * - BulkOperations for multi-select actions
 * - ExtractionProgress for upload feedback
 *
 * This is a complete working example showing how to integrate
 * all Phase B components into a cohesive page.
 */
export default function EnhancedGlossaryPage() {
  const [entries, setEntries] = useState<GlossaryEntry[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [detailEntry, setDetailEntry] = useState<GlossaryEntry | null>(null);
  const [processingTasks, setProcessingTasks] = useState<ProcessingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'cards' | 'list'>('cards');

  // Load glossary entries
  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getGlossaryEntries({ limit: 50 });
      setEntries(data);
    } catch (error) {
      console.error('Failed to load entries:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload for extraction
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Create processing tasks for each file
    const newTasks: ProcessingTask[] = Array.from(files).map((file) => ({
      id: `task-${Date.now()}-${Math.random()}`,
      filename: file.name,
      status: 'queued',
      progress: 0,
    }));

    setProcessingTasks((prev) => [...prev, ...newTasks]);

    // Process each file
    for (const task of newTasks) {
      const file = Array.from(files).find((f) => f.name === task.filename);
      if (!file) continue;

      try {
        // Update to uploading
        updateTaskStatus(task.id, { status: 'uploading', progress: 0 });

        // Simulate upload progress (in real app, use axios progress events)
        for (let i = 0; i <= 100; i += 20) {
          await new Promise((resolve) => setTimeout(resolve, 200));
          updateTaskStatus(task.id, { uploadProgress: i, progress: i / 2 });
        }

        // Upload document
        const uploadedDoc = await apiClient.uploadDocument(file);

        // Update to processing
        updateTaskStatus(task.id, { status: 'processing', progress: 50 });

        // Process document
        const result = await apiClient.processDocument(uploadedDoc.id, {
          language: 'en',
          extract_definitions: true,
        });

        // Simulate processing progress
        for (let i = 0; i <= 100; i += 25) {
          await new Promise((resolve) => setTimeout(resolve, 300));
          updateTaskStatus(task.id, {
            processingProgress: i,
            progress: 50 + i / 2,
          });
        }

        // Mark as completed
        updateTaskStatus(task.id, {
          status: 'completed',
          progress: 100,
          termsExtracted: result.terms_extracted || 0,
          endTime: Date.now(),
        });

        // Refresh entries
        loadEntries();
      } catch (error: any) {
        updateTaskStatus(task.id, {
          status: 'failed',
          error: error.response?.data?.detail || 'Processing failed',
          endTime: Date.now(),
        });
      }
    }
  };

  const updateTaskStatus = (taskId: string, updates: Partial<ProcessingTask>) => {
    setProcessingTasks((prev) =>
      prev.map((task) =>
        task.id === taskId
          ? { ...task, ...updates, startTime: task.startTime || Date.now() }
          : task
      )
    );
  };

  // Selection handlers
  const handleSelect = (id: number, selected: boolean) => {
    setSelectedIds((prev) =>
      selected ? [...prev, id] : prev.filter((i) => i !== id)
    );
  };

  const handleSelectAll = () => {
    setSelectedIds(entries.map((e) => e.id));
  };

  const handleDeselectAll = () => {
    setSelectedIds([]);
  };

  // Entry actions
  const handleEdit = (entry: GlossaryEntry) => {
    console.log('Edit entry:', entry);
    // TODO: Open edit dialog
  };

  const handleDelete = async (id: number) => {
    try {
      await apiClient.deleteGlossaryEntry(id);
      loadEntries();
    } catch (error) {
      console.error('Failed to delete entry:', error);
    }
  };

  const handleViewDetails = (entry: GlossaryEntry) => {
    setDetailEntry(entry);
  };

  const handleClearTask = (taskId: string) => {
    setProcessingTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  return (
    <div className="enhanced-glossary-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Enhanced Glossary</h1>
          <p className="page-description">
            Bilingual term management with advanced UI/UX features
          </p>
        </div>

        <div className="header-actions">
          {/* View Mode Toggle */}
          <div className="view-mode-toggle">
            <button
              className={`mode-button ${viewMode === 'cards' ? 'active' : ''}`}
              onClick={() => setViewMode('cards')}
              title="Card view"
            >
              📇 Cards
            </button>
            <button
              className={`mode-button ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
              title="List view"
            >
              📋 List
            </button>
          </div>

          {/* Upload Button */}
          <label className="upload-button">
            📤 Upload Document
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              multiple
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {/* Extraction Progress */}
      {processingTasks.length > 0 && (
        <ExtractionProgress
          tasks={processingTasks}
          onClear={handleClearTask}
          showCompleted={true}
        />
      )}

      {/* Entries List */}
      <div className="entries-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading glossary entries...</p>
          </div>
        ) : entries.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <h3>No Entries Yet</h3>
            <p>Upload a document to start extracting glossary terms</p>
          </div>
        ) : (
          <div className={`entries-grid ${viewMode}`}>
            {entries.map((entry) => (
              <BilingualCard
                key={entry.id}
                entry={entry}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onSelect={handleSelect}
                selected={selectedIds.includes(entry.id)}
                showCheckbox={true}
                compact={viewMode === 'list'}
              />
            ))}
          </div>
        )}
      </div>

      {/* Bulk Operations Toolbar */}
      <BulkOperations
        selectedIds={selectedIds}
        totalCount={entries.length}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        onRefresh={loadEntries}
      />

      {/* Term Detail Modal */}
      {detailEntry && (
        <div className="detail-modal-overlay" onClick={() => setDetailEntry(null)}>
          <div className="detail-modal-content" onClick={(e) => e.stopPropagation()}>
            <TermDetailView
              entry={detailEntry}
              onClose={() => setDetailEntry(null)}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onRelatedTermClick={(id) => {
                const relatedEntry = entries.find((e) => e.id === id);
                if (relatedEntry) setDetailEntry(relatedEntry);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
