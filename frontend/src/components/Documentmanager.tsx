import { useState } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { useDocument } from '../hooks/useDocument';
import type { DocumentItem } from '../types/document.ts';


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
    totalCount,
    currentPage,
    totalPages,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    clearError,
  } = useDocument();

  // Local UI States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setValidationError(null);
    clearError();
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      
    
      if (file.type !== 'application/pdf') {
        setValidationError('Only PDF documents are supported.');
        setSelectedFile(null);
        return;
      }
      
     
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
     
      const fileInput = document.getElementById('pdf-file') as HTMLInputElement | null;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error('File upload failed:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearchSubmit = (e: FormEvent) => {
    e.preventDefault();
    fetchDocuments(1, searchQuery.trim() || undefined);
  };

  const handlePageChange = (page: number) => {
    fetchDocuments(page, searchQuery.trim() || undefined);
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'ready':
      case 'embedded':
        return 'green';
      case 'processing':
      case 'uploading':
      case 'embedding':
        return 'blue';
      case 'failed':
        return 'red';
      default:
        return '#333';
    }
  };

  return (
    <section aria-labelledby="doc-manager-title" style={{ marginTop: '20px' }}>
      <h3 id="doc-manager-title" style={{ marginBottom: '15px' }}>Document Manager</h3>

      {/* Error state alert */}
      {(validationError || apiError) && (
        <div role="alert" style={{ color: 'red', margin: '15px 0', fontSize: '0.9em' }}>
          <p>{validationError || apiError}</p>
        </div>
      )}

      {}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '25px' }}>
        
        
        <div style={{ background: '#fafafa', padding: '16px', borderRadius: '6px', border: '1px dashed #ccc' }}>
          <form onSubmit={handleUploadSubmit}>
            <label htmlFor="pdf-file" style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', fontSize: '0.9em' }}>
              Upload PDF Study Guide (Max 20MB)
            </label>
            <input
              id="pdf-file"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              disabled={isLoading || isUploading}
              style={{ width: '100%', marginBottom: '12px' }}
            />
            <button 
              type="submit" 
              disabled={!selectedFile || isLoading || isUploading}
              style={{ padding: '6px 12px', cursor: 'pointer', background: '#0066cc', color: '#fff', border: 'none', borderRadius: '4px' }}
            >
              {isUploading ? 'Uploading...' : 'Upload file'}
            </button>
          </form>
        </div>

        {/* Search Form Card */}
        <div style={{ background: '#fafafa', padding: '16px', borderRadius: '6px', border: '1px solid #eee', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <form onSubmit={handleSearchSubmit}>
            <label htmlFor="doc-search" style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', fontSize: '0.9em' }}>
              Search Documents
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                id="doc-search"
                type="search"
                placeholder="Filter by filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ flex: 1, padding: '6px' }}
              />
              <button type="submit" style={{ padding: '6px 12px', cursor: 'pointer' }}>
                Search
              </button>
            </div>
          </form>
        </div>

      </div>

      {/* Documents Table */}
      {isLoading && documents.length === 0 ? (
        <p>Loading files...</p>
      ) : documents.length === 0 ? (
        <p style={{ color: '#888', fontStyle: 'italic', padding: '20px 0' }}>No documents uploaded in this workspace yet.</p>
      ) : (
        <>
          <div style={{ overflowX: 'auto', marginBottom: '15px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95em' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ddd', background: '#f0f0f0', textAlign: 'left' }}>
                  <th style={{ padding: '10px' }}>Filename</th>
                  <th style={{ padding: '10px' }}>Size</th>
                  <th style={{ padding: '10px' }}>Status</th>
                  <th style={{ padding: '10px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc: DocumentItem) => (
                  <tr key={doc.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px', wordBreak: 'break-all' }}>{doc.original_filename}</td>
                    <td style={{ padding: '10px' }}>{formatBytes(doc.file_size)}</td>
                    <td style={{ padding: '10px', textTransform: 'capitalize', fontWeight: 'bold', color: getStatusColor(doc.status) }}>
                      {doc.status}
                    </td>
                    <td style={{ padding: '10px' }}>
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
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
              <button 
                onClick={() => handlePageChange(currentPage - 1)} 
                disabled={currentPage === 1 || isLoading}
                style={{ padding: '5px 10px', cursor: 'pointer' }}
              >
                Previous
              </button>
              <span>Page {currentPage} of {totalPages} ({totalCount} total files)</span>
              <button 
                onClick={() => handlePageChange(currentPage + 1)} 
                disabled={currentPage === totalPages || isLoading}
                style={{ padding: '5px 10px', cursor: 'pointer' }}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
export default DocumentManager;
