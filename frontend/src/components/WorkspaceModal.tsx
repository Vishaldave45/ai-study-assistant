import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { useWorkspace } from '../hooks/useWorkspace.ts';
import { workspaceSchema } from '../modules/Workspace/validation-schema/workspace.schema';
import type { WorkspaceFormData } from '../modules/Workspace/validation-schema/workspace.schema';
import type { WorkspaceSummary } from '../types/workspace.ts';

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
          maxWidth: '90%',
        }}
      >
        <h3 id="modal-title" style={{ marginTop: 0 }}>
          {type === 'create' && 'Create Workspace'}
          {type === 'edit' && `Rename Workspace "${workspace?.name}"`}
          {type === 'delete' && 'Delete Workspace'}
        </h3>

        {apiError && (
          <div role="alert" style={{ color: 'red', margin: '10px 0', fontSize: '0.9em' }}>
            <p>{apiError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          {type === 'delete' ? (
            <p style={{ margin: '15px 0', fontSize: '0.95em', color: '#c00' }}>
              Are you sure you want to delete <strong>{workspace?.name}</strong>? This action is permanent and will delete all documents and study materials.
            </p>
          ) : (
            <>
              <div style={{ marginBottom: '12px' }}>
                <label htmlFor="ws-name" style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em' }}>
                  Workspace Name
                </label>
                <input
                  id="ws-name"
                  type="text"
                  {...register('name')}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderColor: errors.name ? '#ef4444' : '#ccc',
                    borderRadius: '4px',
                    borderStyle: 'solid',
                    borderWidth: '1px',
                  }}
                />
                {errors.name && (
                  <p style={{ color: '#ef4444', fontSize: '0.8em', marginTop: '4px' }}>
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label htmlFor="ws-desc" style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em' }}>
                  Description (Optional)
                </label>
                <textarea
                  id="ws-desc"
                  {...register('description')}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '8px',
                    minHeight: '80px',
                    resize: 'vertical',
                    borderColor: errors.description ? '#ef4444' : '#ccc',
                    borderRadius: '4px',
                    borderStyle: 'solid',
                    borderWidth: '1px',
                  }}
                />
                {errors.description && (
                  <p style={{ color: '#ef4444', fontSize: '0.8em', marginTop: '4px' }}>
                    {errors.description.message}
                  </p>
                )}
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
