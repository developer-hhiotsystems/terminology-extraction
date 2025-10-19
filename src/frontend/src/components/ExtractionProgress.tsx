import { useState, useEffect } from 'react';
import './ExtractionProgress.css';

export interface ProcessingTask {
  id: string;
  filename: string;
  status: 'queued' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  uploadProgress?: number; // 0-100 for upload phase
  processingProgress?: number; // 0-100 for processing phase
  termsExtracted?: number;
  error?: string;
  startTime?: number;
  endTime?: number;
}

interface ExtractionProgressProps {
  tasks: ProcessingTask[];
  onCancel?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
  onClear?: (taskId: string) => void;
  showCompleted?: boolean;
  compact?: boolean;
}

/**
 * ExtractionProgress Component
 *
 * Displays real-time feedback for document upload and term extraction:
 * - Upload progress with percentage
 * - Processing status with stages
 * - Error feedback with retry option
 * - Success indicators with extracted term count
 * - Queue management for multiple files
 * - Time elapsed/estimated
 *
 * Perfect for providing user feedback during async operations
 */
export default function ExtractionProgress({
  tasks,
  onCancel,
  onRetry,
  onClear,
  showCompleted = true,
  compact = false,
}: ExtractionProgressProps) {
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());

  // Filter tasks based on showCompleted
  const visibleTasks = showCompleted
    ? tasks
    : tasks.filter(t => t.status !== 'completed' && t.status !== 'failed');

  // Auto-expand active tasks
  useEffect(() => {
    const activeTasks = tasks.filter(
      t => t.status === 'uploading' || t.status === 'processing'
    );
    const newExpanded = new Set(expandedTasks);
    activeTasks.forEach(t => newExpanded.add(t.id));
    setExpandedTasks(newExpanded);
  }, [tasks]);

  const toggleExpanded = (taskId: string) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedTasks(newExpanded);
  };

  const getStatusIcon = (status: ProcessingTask['status']) => {
    switch (status) {
      case 'queued':
        return '⏱️';
      case 'uploading':
        return '📤';
      case 'processing':
        return '⚙️';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
    }
  };

  const getStatusLabel = (status: ProcessingTask['status']) => {
    switch (status) {
      case 'queued':
        return 'Queued';
      case 'uploading':
        return 'Uploading...';
      case 'processing':
        return 'Extracting Terms...';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
    }
  };

  const getStatusClass = (status: ProcessingTask['status']) => {
    switch (status) {
      case 'queued':
        return 'status-queued';
      case 'uploading':
      case 'processing':
        return 'status-active';
      case 'completed':
        return 'status-completed';
      case 'failed':
        return 'status-failed';
    }
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getElapsedTime = (task: ProcessingTask) => {
    if (!task.startTime) return null;
    const endTime = task.endTime || Date.now();
    return formatTime(endTime - task.startTime);
  };

  const getProcessingStage = (task: ProcessingTask) => {
    if (task.status === 'uploading') {
      return 'Uploading document...';
    }
    if (task.status === 'processing') {
      const progress = task.processingProgress || 0;
      if (progress < 20) return 'Analyzing document structure...';
      if (progress < 40) return 'Extracting text content...';
      if (progress < 60) return 'Identifying terms...';
      if (progress < 80) return 'Extracting definitions...';
      return 'Finalizing extraction...';
    }
    return null;
  };

  // Calculate overall statistics
  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => t.status === 'failed').length,
    active: tasks.filter(t => t.status === 'uploading' || t.status === 'processing').length,
    queued: tasks.filter(t => t.status === 'queued').length,
  };

  if (visibleTasks.length === 0) {
    return null;
  }

  return (
    <div className={`extraction-progress-container ${compact ? 'compact' : ''}`}>
      {/* Header */}
      {!compact && (
        <div className="progress-header">
          <h3 className="progress-title">Document Processing</h3>
          <div className="progress-stats">
            {stats.active > 0 && (
              <span className="stat-badge stat-active">
                {stats.active} active
              </span>
            )}
            {stats.queued > 0 && (
              <span className="stat-badge stat-queued">
                {stats.queued} queued
              </span>
            )}
            {stats.completed > 0 && (
              <span className="stat-badge stat-completed">
                {stats.completed} completed
              </span>
            )}
            {stats.failed > 0 && (
              <span className="stat-badge stat-failed">
                {stats.failed} failed
              </span>
            )}
          </div>
        </div>
      )}

      {/* Tasks List */}
      <div className="progress-tasks-list">
        {visibleTasks.map((task) => {
          const isExpanded = expandedTasks.has(task.id);
          const stage = getProcessingStage(task);
          const elapsed = getElapsedTime(task);

          return (
            <div
              key={task.id}
              className={`progress-task ${getStatusClass(task.status)} ${
                isExpanded ? 'expanded' : ''
              }`}
            >
              {/* Task Header */}
              <div
                className="task-header"
                onClick={() => toggleExpanded(task.id)}
              >
                <div className="task-info">
                  <span className="task-icon">{getStatusIcon(task.status)}</span>
                  <div className="task-details">
                    <div className="task-filename">{task.filename}</div>
                    <div className="task-status">
                      {getStatusLabel(task.status)}
                      {elapsed && <span className="task-time"> • {elapsed}</span>}
                    </div>
                  </div>
                </div>

                <div className="task-actions">
                  {task.status === 'completed' && task.termsExtracted !== undefined && (
                    <span className="terms-badge">
                      {task.termsExtracted} terms
                    </span>
                  )}
                  {(task.status === 'uploading' || task.status === 'processing') && onCancel && (
                    <button
                      className="task-action-button cancel-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onCancel(task.id);
                      }}
                      title="Cancel"
                    >
                      ✕
                    </button>
                  )}
                  {task.status === 'failed' && onRetry && (
                    <button
                      className="task-action-button retry-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRetry(task.id);
                      }}
                      title="Retry"
                    >
                      🔄
                    </button>
                  )}
                  {(task.status === 'completed' || task.status === 'failed') && onClear && (
                    <button
                      className="task-action-button clear-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onClear(task.id);
                      }}
                      title="Clear"
                    >
                      🗑️
                    </button>
                  )}
                  <button className="task-expand-button">
                    {isExpanded ? '▼' : '▶'}
                  </button>
                </div>
              </div>

              {/* Progress Bar */}
              {(task.status === 'uploading' || task.status === 'processing') && (
                <div className="task-progress-bar">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${task.progress}%` }}
                  >
                    <span className="progress-percentage">{task.progress}%</span>
                  </div>
                </div>
              )}

              {/* Expanded Details */}
              {isExpanded && (
                <div className="task-expanded-details">
                  {stage && (
                    <div className="detail-row">
                      <span className="detail-label">Current Stage:</span>
                      <span className="detail-value">{stage}</span>
                    </div>
                  )}

                  {task.status === 'processing' && task.processingProgress !== undefined && (
                    <div className="detail-row">
                      <span className="detail-label">Processing:</span>
                      <div className="detail-progress">
                        <div className="mini-progress-bar">
                          <div
                            className="mini-progress-fill"
                            style={{ width: `${task.processingProgress}%` }}
                          ></div>
                        </div>
                        <span className="mini-progress-label">
                          {task.processingProgress}%
                        </span>
                      </div>
                    </div>
                  )}

                  {task.status === 'uploading' && task.uploadProgress !== undefined && (
                    <div className="detail-row">
                      <span className="detail-label">Upload:</span>
                      <div className="detail-progress">
                        <div className="mini-progress-bar">
                          <div
                            className="mini-progress-fill"
                            style={{ width: `${task.uploadProgress}%` }}
                          ></div>
                        </div>
                        <span className="mini-progress-label">
                          {task.uploadProgress}%
                        </span>
                      </div>
                    </div>
                  )}

                  {task.error && (
                    <div className="detail-row error-row">
                      <span className="detail-label">Error:</span>
                      <span className="detail-error">{task.error}</span>
                    </div>
                  )}

                  {task.status === 'completed' && (
                    <div className="detail-row success-row">
                      <span className="detail-label">Result:</span>
                      <span className="detail-success">
                        Successfully extracted {task.termsExtracted || 0} glossary terms
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
