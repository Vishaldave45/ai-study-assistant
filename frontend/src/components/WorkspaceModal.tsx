import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { useWorkspace } from '../hooks/useWorkspace.ts';
import type { WorkspaceSummary } from '../types/workspace.ts';

interface WorkspaceModalProps {
  type: 'create' | 'edit' | 'delete';
  workspace: WorkspaceSummary | null;
  onClose: () => void;
}

export function WorkspaceModal({ type, workspace, onClose }: WorkspaceModalProps) {
  const { createWorkspace, updateWorkspace, deleteWorkspace, error: apiError, clearError, isLoading } = useWorkspace();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Initialize fields on open (e.g. for Rename / Edit modal)
  useEffect(() => {
    clearError();
    setValidationError(null);
    if (type === 'edit' && workspace) {
      setName(workspace.name);
      setDescription(workspace.description || '');
    } else {
      setName('');
      setDescription('');
    }
  }, [type, workspace]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError(null);

    // Skip validation for Delete action
    if (type !== 'delete') {
      if (!name.trim()) {
        setValidationError('Workspace name is required.');
        return;
      }
      if (name.length > 255) {
        setValidationError('Workspace name cannot exceed 255 characters.');
        return;
      }
      if (description.length > 1000) {
        setValidationError('Description cannot exceed 1000 characters.');
        return;
      }
    }

    try {
      if (type === 'create') {
        await createWorkspace({ name: name.trim(), description: description.trim() || undefined });
      } else if (type === 'edit' && workspace) {
        await updateWorkspace(workspace.id, { name: name.trim(), description: description.trim() || undefined });
      } else if (type === 'delete' && workspace) {
        await deleteWorkspace(workspace.id);
      }
      onClose();
    } catch (err) {
      console.error(`Workspace ${type} failed:`, err);
    }
  };

  return (
    <div 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="modal-title"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div 
        style={{ 
          background: '#fff', 
          padding: '24px', 
          borderRadius: '8px', 
          width: '400px', 
          maxWidth: '90%' 
        }}
      >
        <h3 id="modal-title" style={{ marginTop: 0 }}>
          {type === 'create' && 'Create Workspace'}
          {type === 'edit' && `Rename Workspace "${workspace?.name}"`}
          {type === 'delete' && 'Delete Workspace'}
        </h3>

        {(validationError || apiError) && (
          <div role="alert" style={{ color: 'red', margin: '10px 0', fontSize: '0.9em' }}>
            <p>{validationError || apiError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {type === 'delete' ? (
            <p style={{ margin: '15px 0', fontSize: '0.95em', color: '#c00' }}>
              Are you sure you want to delete <strong>{workspace?.name}</strong>? This action is permanent and will delete all documents and study materials.
            </p>
          ) : (
            <>
              <div style={{ marginBottom: '12px' }}>
                <label htmlFor="ws-name" style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em' }}>Workspace Name</label>
                <input
                  id="ws-name"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    if (validationError) setValidationError(null);
                  }}
                  disabled={isLoading}
                  required
                  style={{ width: '100%', padding: '8px' }}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label htmlFor="ws-desc" style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em' }}>Description (Optional)</label>
                <textarea
                  id="ws-desc"
                  value={description}
                  onChange={(e) => {
                    setDescription(e.target.value);
                    if (validationError) setValidationError(null);
                  }}
                  disabled={isLoading}
                  style={{ width: '100%', padding: '8px', minHeight: '80px', resize: 'vertical' }}
                />
              </div>
            </>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button 
              type="button" 
              onClick={onClose} 
              disabled={isLoading} 
              style={{ padding: '6px 12px', cursor: 'pointer' }}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={isLoading} 
              style={{ 
                padding: '6px 12px', 
                cursor: 'pointer',
                background: type === 'delete' ? '#c00' : '#0066cc',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
              }}
            >
              {isLoading ? 'Processing...' : type === 'delete' ? 'Delete' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
export default WorkspaceModal;
