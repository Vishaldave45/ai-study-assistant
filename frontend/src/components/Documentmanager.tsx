import { useReducer, useMemo, memo } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { useDocument } from '../hooks/useDocument';
import { DataTable } from './DataTable/DataTable';
import type { DocumentItem } from '../types/document.ts';

// Helper to format file sizes nicely
function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// State & Reducer for document upload workflow
interface UploadState {
  selectedFile: File | null;
  validationError: string | null;
  isUploading: boolean;
}

type UploadAction =
  | { type: 'SELECT_FILE'; payload: File }
  | { type: 'CLEAR_FILE' }
  | { type: 'SET_VALIDATION_ERROR'; payload: string }
  | { type: 'START_UPLOADING' }
  | { type: 'UPLOAD_SUCCESS' }
  | { type: 'UPLOAD_FAILURE' };

const initialUploadState: UploadState = {
  selectedFile: null,
  validationError: null,
  isUploading: false,
};

function uploadReducer(state: UploadState, action: UploadAction): UploadState {
  switch (action.type) {
    case 'SELECT_FILE':
      return { ...state, selectedFile: action.payload, validationError: null };
    case 'CLEAR_FILE':
      return { ...state, selectedFile: null, validationError: null };
    case 'SET_VALIDATION_ERROR':
      return { ...state, selectedFile: null, validationError: action.payload };
    case 'START_UPLOADING':
      return { ...state, isUploading: true, validationError: null };
    case 'UPLOAD_SUCCESS':
      return { ...state, isUploading: false, selectedFile: null, validationError: null };
    case 'UPLOAD_FAILURE':
      return { ...state, isUploading: false };
    default:
      return state;
  }
}

export const DocumentManager = memo(function DocumentManager() {
  const {
    documents,
    isLoading,
    error: apiError,
    uploadDocument,
    deleteDocument,
    clearError,
  } = useDocument();

  const [state, dispatch] = useReducer(uploadReducer, initialUploadState);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    clearError();
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];

      if (file.type !== 'application/pdf') {
        dispatch({ type: 'SET_VALIDATION_ERROR', payload: 'Only PDF documents are supported.' });
        return;
      }

      if (file.size > 20 * 1024 * 1024) {
        dispatch({ type: 'SET_VALIDATION_ERROR', payload: 'File size exceeds the 20MB limit.' });
        return;
      }

      dispatch({ type: 'SELECT_FILE', payload: file });
    }
  };

  const handleUploadSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    if (!state.selectedFile) {
      dispatch({ type: 'SET_VALIDATION_ERROR', payload: 'Please select a PDF file first.' });
      return;
    }

    dispatch({ type: 'START_UPLOADING' });
    try {
      await uploadDocument(state.selectedFile);
      dispatch({ type: 'UPLOAD_SUCCESS' });
      const fileInput = document.getElementById('pdf-file') as HTMLInputElement | null;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error('File upload failed:', err);
      dispatch({ type: 'UPLOAD_FAILURE' });
    }
  };

  const columns = useMemo<ColumnDef<DocumentItem>[]>(
    () => [
      {
        accessorKey: 'original_filename',
        header: 'Filename',
        cell: (info: any) => (
          <div style={{ fontWeight: 600, wordBreak: 'break-all' }}>
            📄 {info.getValue()}
          </div>
        ),
      },
      {
        accessorKey: 'file_size',
        header: 'Size',
        cell: (info: any) => formatBytes(info.getValue()),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info: any) => {
          const status = info.getValue() as string;
          const colorClass =
            status === 'ready' || status === 'embedded'
              ? 'green'
              : status === 'failed'
              ? 'red'
              : 'blue';
          return <span className={`status-pill ${colorClass}`}>{status}</span>;
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Uploaded Date',
        cell: (info: any) => new Date(info.getValue()).toLocaleDateString(),
      },
      {
        id: 'actions',
        header: 'Actions',
        enableSorting: false,
        enableColumnFilter: false,
        cell: (info: any) => {
          const doc = info.row.original as DocumentItem;
          return (
            <div style={{ display: 'flex', gap: '8px' }}>
              <a
                href={`/api/v1/documents/${doc.id}/download`}
                download
                title="Download PDF"
                style={{ textDecoration: 'none', fontSize: '1.1em' }}
              >
                📥
              </a>
              <button
                onClick={() => deleteDocument(doc.id)}
                title="Delete PDF"
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1em' }}
              >
                🗑️
              </button>
            </div>
          );
        },
      },
    ],
    [deleteDocument]
  );

  const handleDeleteSelectedRows = (selectedRows: DocumentItem[]) => {
    selectedRows.forEach((doc) => deleteDocument(doc.id));
  };

  return (
    <section aria-labelledby="doc-manager-title" style={{ marginTop: '10px' }}>
      <h3 id="doc-manager-title" style={{ marginBottom: '15px' }}>Document Manager</h3>

      {(state.validationError || apiError) && (
        <div role="alert" style={{ color: 'red', margin: '15px 0', fontSize: '0.9em' }}>
          <p>{state.validationError || apiError}</p>
        </div>
      )}

      <div style={{ background: '#fafafa', padding: '16px', borderRadius: '8px', border: '1px dashed #ccc', marginBottom: '20px' }}>
        <form onSubmit={handleUploadSubmit}>
          <label htmlFor="pdf-file" style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', fontSize: '0.9em' }}>
            Upload PDF Study Guide (Max 20MB)
          </label>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input
              id="pdf-file"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              disabled={isLoading || state.isUploading}
              style={{ flex: 1 }}
            />
            <button
              type="submit"
              disabled={!state.selectedFile || isLoading || state.isUploading}
              style={{ padding: '8px 16px', cursor: 'pointer', background: '#0066cc', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: '600' }}
            >
              {state.isUploading ? 'Uploading...' : 'Upload File'}
            </button>
          </div>
        </form>
      </div>

      <DataTable
        columns={columns}
        data={documents}
        title="Workspace Documents"
        subtitle="Manage uploaded PDF files with sorting, global search, column filtering, and row selection."
        isLoading={isLoading}
        onDeleteSelectedRows={handleDeleteSelectedRows}
      />
    </section>
  );
});

export default DocumentManager;
