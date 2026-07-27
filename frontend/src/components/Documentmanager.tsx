import { useState, useMemo } from 'react';
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

export function DocumentManager() {
  const {
    documents,
    isLoading,
    error: apiError,
    uploadDocument,
    deleteDocument,
    clearError,
  } = useDocument();

  // Local UI States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setValidationError(null);
    clearError();
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      
      // Validation: Must be PDF
      if (file.type !== 'application/pdf') {
        setValidationError('Only PDF documents are supported.');
        setSelectedFile(null);
        return;
      }
      
      // Validation: Max 20MB
      if (file.size > 20 * 1024 * 1024) {
        setValidationError('File size exceeds the 20MB limit.');
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleUploadSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!selectedFile) {
      setValidationError('Please select a PDF file first.');
      return;
    }

    setIsUploading(true);
    try {
      await uploadDocument(selectedFile);
      setSelectedFile(null);
      // Reset file input element manually
      const fileInput = document.getElementById('pdf-file') as HTMLInputElement | null;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error('File upload failed:', err);
    } finally {
      setIsUploading(false);
    }
  };

  // TanStack Table Column Definitions
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

      {/* Error state alert */}
      {(validationError || apiError) && (
        <div role="alert" style={{ color: 'red', margin: '15px 0', fontSize: '0.9em' }}>
          <p>{validationError || apiError}</p>
        </div>
      )}

      {/* Upload PDF Card */}
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
              disabled={isLoading || isUploading}
              style={{ flex: 1 }}
            />
            <button 
              type="submit" 
              disabled={!selectedFile || isLoading || isUploading}
              style={{ padding: '8px 16px', cursor: 'pointer', background: '#0066cc', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: '600' }}
            >
              {isUploading ? 'Uploading...' : 'Upload File'}
            </button>
          </div>
        </form>
      </div>

      {/* Documents TanStack Table */}
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
}
export default DocumentManager;
