import { useState } from 'react';
import apiClient from '../api/client';
import './BulkOperations.css';

interface BulkOperationsProps {
  selectedIds: number[];
  totalCount: number;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onRefresh?: () => void;
}

type BulkAction = 'validate' | 'reject' | 'pending' | 'export' | 'delete';

/**
 * BulkOperations Component
 *
 * Floating toolbar for bulk actions on selected glossary entries:
 * - Select all / deselect all
 * - Bulk validation status update (validated/pending/rejected)
 * - Bulk export (CSV, Excel, JSON)
 * - Bulk delete with confirmation
 * - Progress feedback
 * - Undo capability (TODO)
 *
 * Displays when one or more items are selected
 */
export default function BulkOperations({
  selectedIds,
  totalCount,
  onSelectAll,
  onDeselectAll,
  onRefresh,
}: BulkOperationsProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingAction, setPendingAction] = useState<BulkAction | null>(null);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  // Don't show if no items selected
  if (selectedIds.length === 0) {
    return null;
  }

  const performBulkAction = async (action: BulkAction) => {
    setIsProcessing(true);
    setResult(null);

    try {
      switch (action) {
        case 'validate':
        case 'reject':
        case 'pending': {
          const statusMap: Record<string, 'validated' | 'rejected' | 'pending'> = {
            validate: 'validated',
            reject: 'rejected',
            pending: 'pending',
          };
          const status = statusMap[action];

          const response = await apiClient.bulkUpdateEntries(selectedIds, status);
          setResult({
            success: true,
            message: `${response.updated_count} entries marked as ${status}`,
          });
          onRefresh?.();
          break;
        }

        case 'export': {
          // Export as JSON by default (could expand to CSV/Excel)
          const blob = await apiClient.exportGlossary('json', {});
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `glossary-export-${new Date().toISOString().split('T')[0]}.json`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          setResult({
            success: true,
            message: `${selectedIds.length} entries exported`,
          });
          break;
        }

        case 'delete': {
          // Delete all selected entries
          await Promise.all(
            selectedIds.map(id => apiClient.deleteGlossaryEntry(id))
          );
          setResult({
            success: true,
            message: `${selectedIds.length} entries deleted`,
          });
          onRefresh?.();
          onDeselectAll();
          break;
        }
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || `Failed to ${action} entries`,
      });
    } finally {
      setIsProcessing(false);
      setShowConfirmDialog(false);
      setPendingAction(null);

      // Auto-hide success message after 3 seconds
      if (result?.success) {
        setTimeout(() => setResult(null), 3000);
      }
    }
  };

  const handleActionClick = (action: BulkAction) => {
    // Confirm destructive actions
    if (action === 'delete' || action === 'reject') {
      setPendingAction(action);
      setShowConfirmDialog(true);
    } else {
      performBulkAction(action);
    }
  };

  const confirmAction = () => {
    if (pendingAction) {
      performBulkAction(pendingAction);
    }
  };

  const cancelAction = () => {
    setShowConfirmDialog(false);
    setPendingAction(null);
  };

  const getConfirmMessage = () => {
    if (pendingAction === 'delete') {
      return `Are you sure you want to delete ${selectedIds.length} ${
        selectedIds.length === 1 ? 'entry' : 'entries'
      }? This action cannot be undone.`;
    }
    if (pendingAction === 'reject') {
      return `Mark ${selectedIds.length} ${
        selectedIds.length === 1 ? 'entry' : 'entries'
      } as rejected?`;
    }
    return '';
  };

  return (
    <>
      {/* Bulk Operations Toolbar */}
      <div className="bulk-operations-toolbar">
        {/* Selection Info */}
        <div className="bulk-selection-info">
          <span className="selection-count">
            {selectedIds.length} selected
          </span>
          {selectedIds.length !== totalCount && (
            <button
              className="select-action-button"
              onClick={onSelectAll}
              disabled={isProcessing}
            >
              Select all ({totalCount})
            </button>
          )}
          {selectedIds.length > 0 && (
            <button
              className="select-action-button"
              onClick={onDeselectAll}
              disabled={isProcessing}
            >
              Deselect all
            </button>
          )}
        </div>

        {/* Action Buttons */}
        <div className="bulk-actions">
          <button
            className="bulk-action-button action-validate"
            onClick={() => handleActionClick('validate')}
            disabled={isProcessing}
            title="Mark as validated"
          >
            ✓ Validate
          </button>

          <button
            className="bulk-action-button action-pending"
            onClick={() => handleActionClick('pending')}
            disabled={isProcessing}
            title="Mark as pending review"
          >
            ⏳ Pending
          </button>

          <button
            className="bulk-action-button action-reject"
            onClick={() => handleActionClick('reject')}
            disabled={isProcessing}
            title="Mark as rejected"
          >
            ✗ Reject
          </button>

          <div className="action-divider"></div>

          <button
            className="bulk-action-button action-export"
            onClick={() => handleActionClick('export')}
            disabled={isProcessing}
            title="Export selected entries"
          >
            📥 Export
          </button>

          <button
            className="bulk-action-button action-delete"
            onClick={() => handleActionClick('delete')}
            disabled={isProcessing}
            title="Delete selected entries"
          >
            🗑️ Delete
          </button>
        </div>

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="bulk-processing">
            <div className="processing-spinner"></div>
            <span>Processing...</span>
          </div>
        )}
      </div>

      {/* Result Toast */}
      {result && (
        <div className={`bulk-result-toast ${result.success ? 'success' : 'error'}`}>
          <span className="toast-icon">
            {result.success ? '✅' : '❌'}
          </span>
          <span className="toast-message">{result.message}</span>
          <button
            className="toast-close"
            onClick={() => setResult(null)}
          >
            ✕
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="bulk-confirm-overlay" onClick={cancelAction}>
          <div
            className="bulk-confirm-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="confirm-header">
              <h3 className="confirm-title">Confirm Action</h3>
              <button
                className="confirm-close"
                onClick={cancelAction}
              >
                ✕
              </button>
            </div>

            <div className="confirm-body">
              <div className="confirm-icon">
                {pendingAction === 'delete' ? '⚠️' : '❓'}
              </div>
              <p className="confirm-message">{getConfirmMessage()}</p>
            </div>

            <div className="confirm-actions">
              <button
                className="confirm-button cancel-button"
                onClick={cancelAction}
              >
                Cancel
              </button>
              <button
                className={`confirm-button confirm-button-primary ${
                  pendingAction === 'delete' ? 'danger' : ''
                }`}
                onClick={confirmAction}
              >
                {pendingAction === 'delete' ? 'Delete' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
