import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { useWorkspace } from '../../hooks/useWorkspace';
import { workspaceSchema } from '../../modules/Workspace/validation-schema/workspace.schema';
import type { WorkspaceFormData } from '../../modules/Workspace/validation-schema/workspace.schema';
import type { WorkspaceSummary } from '../../types/workspace';

interface WorkspaceModalProps {
  type: 'create' | 'edit' | 'delete';
  workspace: WorkspaceSummary | null;
  onClose: () => void;
}

export function WorkspaceModal({ type, workspace, onClose }: WorkspaceModalProps) {
  const { createWorkspace, updateWorkspace, deleteWorkspace, error: apiError, clearError, isLoading } = useWorkspace();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<WorkspaceFormData>({
    resolver: type !== 'delete' ? yupResolver(workspaceSchema) : undefined,
    mode: 'onTouched',
    defaultValues: {
      name: '',
      description: '',
    },
  });

  useEffect(() => {
    clearError();
    if (type === 'edit' && workspace) {
      setValue('name', workspace.name);
      setValue('description', workspace.description || '');
    } else {
      reset({ name: '', description: '' });
    }
  }, [type, workspace, clearError, setValue, reset]);

  const onSubmit = async (data: WorkspaceFormData) => {
    clearError();
    try {
      if (type === 'create') {
        await createWorkspace({ name: data.name.trim(), description: data.description?.trim() || undefined });
      } else if (type === 'edit' && workspace) {
        await updateWorkspace(workspace.id, { name: data.name.trim(), description: data.description?.trim() || undefined });
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
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        className="ws-modal-card"
        style={{
          background: '#ffffff',
          color: '#0f172a',
          padding: '24px',
          borderRadius: '12px',
          width: '420px',
          maxWidth: '90%',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1)',
        }}
      >
        <h3 id="modal-title" className="ws-modal-title" style={{ marginTop: 0, color: '#0f172a', fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px' }}>
          {type === 'create' && 'Create Workspace'}
          {type === 'edit' && `Rename Workspace "${workspace?.name}"`}
          {type === 'delete' && 'Delete Workspace'}
        </h3>

        {apiError && (
          <div role="alert" style={{ color: '#dc2626', background: '#fef2f2', border: '1px solid #fecaca', padding: '10px 14px', borderRadius: '6px', margin: '10px 0', fontSize: '0.85em' }}>
            <p>{apiError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          {type === 'delete' ? (
            <p style={{ margin: '15px 0', fontSize: '0.95em', color: '#dc2626' }}>
              Are you sure you want to delete <strong style={{ color: '#0f172a' }}>{workspace?.name}</strong>? This action is permanent and will delete all documents and study materials.
            </p>
          ) : (
            <>
              <div style={{ marginBottom: '16px' }}>
                <label htmlFor="ws-name" className="ws-modal-label" style={{ display: 'block', marginBottom: '6px', fontSize: '0.9rem', fontWeight: 600, color: '#1e293b' }}>
                  Workspace Name
                </label>
                <input
                  id="ws-name"
                  type="text"
                  className="ws-modal-input"
                  {...register('name')}
                  disabled={isLoading}
                  placeholder="e.g. Computer Networks & Security"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    color: '#0f172a',
                    backgroundColor: '#ffffff',
                    borderColor: errors.name ? '#ef4444' : '#94a3b8',
                    borderRadius: '6px',
                    borderStyle: 'solid',
                    borderWidth: '1.5px',
                    fontSize: '0.9em',
                    outline: 'none',
                  }}
                />
                {errors.name && (
                  <p style={{ color: '#ef4444', fontSize: '0.8em', marginTop: '4px', fontWeight: 500 }}>
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label htmlFor="ws-desc" className="ws-modal-label" style={{ display: 'block', marginBottom: '6px', fontSize: '0.9rem', fontWeight: 600, color: '#1e293b' }}>
                  Description (Optional)
                </label>
                <textarea
                  id="ws-desc"
                  className="ws-modal-textarea"
                  {...register('description')}
                  disabled={isLoading}
                  placeholder="Workspace purpose or notes..."
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    color: '#0f172a',
                    backgroundColor: '#ffffff',
                    minHeight: '84px',
                    resize: 'vertical',
                    borderColor: errors.description ? '#ef4444' : '#94a3b8',
                    borderRadius: '6px',
                    borderStyle: 'solid',
                    borderWidth: '1.5px',
                    fontSize: '0.9em',
                    outline: 'none',
                  }}
                />
                {errors.description && (
                  <p style={{ color: '#ef4444', fontSize: '0.8em', marginTop: '4px', fontWeight: 500 }}>
                    {errors.description.message}
                  </p>
                )}
              </div>
            </>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              style={{
                padding: '8px 16px',
                cursor: 'pointer',
                background: '#f1f5f9',
                color: '#334155',
                border: '1px solid #cbd5e1',
                borderRadius: '6px',
                fontWeight: 600,
                fontSize: '0.88em',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              style={{
                padding: '8px 18px',
                cursor: 'pointer',
                background: type === 'delete' ? '#dc2626' : '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                fontWeight: 600,
                fontSize: '0.88em',
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
