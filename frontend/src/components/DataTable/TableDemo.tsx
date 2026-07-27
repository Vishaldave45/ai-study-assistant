import { useState, useMemo } from 'react';
import type { ColumnDef, PaginationState, SortingState } from '@tanstack/react-table';
import { DataTable } from './DataTable';
import { useServerDocumentsQuery } from '../../hooks/useServerDocumentsQuery';
import { useWorkspace } from '../../hooks/useWorkspace';
import type { DocumentItem } from '../../types/document.ts';

// Sample mock data for client-side table demonstration
interface StudyMaterial {
  id: string;
  title: string;
  category: string;
  author: string;
  pages: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  status: 'Published' | 'Draft' | 'Archived';
  lastUpdated: string;
}

const MOCK_MATERIALS: StudyMaterial[] = [
  { id: '1', title: 'Quantum Physics Fundamentals', category: 'Physics', author: 'Dr. Dave', pages: 42, difficulty: 'Advanced', status: 'Published', lastUpdated: '2026-07-20' },
  { id: '2', title: 'Linear Algebra Cheat Sheet', category: 'Mathematics', author: 'Prof. Alice', pages: 12, difficulty: 'Intermediate', status: 'Published', lastUpdated: '2026-07-22' },
  { id: '3', title: 'Organic Chemistry Reactions', category: 'Chemistry', author: 'Dr. Smith', pages: 85, difficulty: 'Advanced', status: 'Draft', lastUpdated: '2026-07-24' },
  { id: '4', title: 'Introduction to Machine Learning', category: 'Computer Science', author: 'AI Assistant', pages: 120, difficulty: 'Beginner', status: 'Published', lastUpdated: '2026-07-25' },
  { id: '5', title: 'World History Timeline (1900-2000)', category: 'History', author: 'Prof. H. Wells', pages: 30, difficulty: 'Beginner', status: 'Archived', lastUpdated: '2026-06-15' },
  { id: '6', title: 'Data Structures & Algorithms', category: 'Computer Science', author: 'Tech Academy', pages: 95, difficulty: 'Intermediate', status: 'Published', lastUpdated: '2026-07-26' },
  { id: '7', title: 'Macroeconomics Principles', category: 'Economics', author: 'Dr. Keynes', pages: 64, difficulty: 'Intermediate', status: 'Published', lastUpdated: '2026-07-18' },
  { id: '8', title: 'Cell Biology Notes', category: 'Biology', author: 'Dr. Dave', pages: 28, difficulty: 'Beginner', status: 'Draft', lastUpdated: '2026-07-21' },
];

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function TableDemo() {
  const [activeTab, setActiveTab] = useState<'server' | 'client'>('server');
  const [clientData, setClientData] = useState<StudyMaterial[]>(MOCK_MATERIALS);

  // Server-side State
  const { activeWorkspace } = useWorkspace();
  const [serverPagination, setServerPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [serverSorting, setServerSorting] = useState<SortingState>([]);
  const [serverGlobalFilter, setServerGlobalFilter] = useState('');

  // Server-side React Query integration
  const {
    data: serverDocResponse,
    isLoading: isServerLoading,
    deleteDocument,
  } = useServerDocumentsQuery({
    workspaceId: activeWorkspace?.id || null,
    page: serverPagination.pageIndex + 1,
    pageSize: serverPagination.pageSize,
    query: serverGlobalFilter,
  });

  // Client-side Columns Definition
  const clientColumns = useMemo<ColumnDef<StudyMaterial>[]>(
    () => [
      {
        accessorKey: 'title',
        header: 'Title',
        cell: (info: any) => <strong>{info.getValue()}</strong>,
      },
      {
        accessorKey: 'category',
        header: 'Category',
        cell: (info: any) => (
          <span className="badge category-badge">{info.getValue()}</span>
        ),
      },
      {
        accessorKey: 'author',
        header: 'Author',
      },
      {
        accessorKey: 'pages',
        header: 'Pages',
      },
      {
        accessorKey: 'difficulty',
        header: 'Difficulty',
        cell: (info: any) => {
          const val = info.getValue();
          const colorClass = val === 'Beginner' ? 'green' : val === 'Intermediate' ? 'orange' : 'purple';
          return <span className={`status-pill ${colorClass}`}>{val}</span>;
        },
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info: any) => {
          const status = info.getValue();
          const colorClass = status === 'Published' ? 'green' : status === 'Draft' ? 'blue' : 'gray';
          return <span className={`status-pill ${colorClass}`}>{status}</span>;
        },
      },
      {
        accessorKey: 'lastUpdated',
        header: 'Last Updated',
      },
    ],
    []
  );

  // Server-side Documents Columns Definition
  const serverColumns = useMemo<ColumnDef<DocumentItem>[]>(
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
          const status = info.getValue();
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
          const doc = info.row.original;
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

  const handleDeleteClientRows = (selectedRows: StudyMaterial[]) => {
    const selectedIds = new Set(selectedRows.map((r) => r.id));
    setClientData((prev) => prev.filter((item) => !selectedIds.has(item.id)));
  };

  const handleDeleteServerRows = (selectedRows: DocumentItem[]) => {
    selectedRows.forEach((doc) => deleteDocument(doc.id));
  };

  return (
    <div style={{ padding: '20px 0' }}>
      {/* Mode Switcher Tabs */}
      <div className="tab-switcher">
        <button
          className={`tab-btn ${activeTab === 'server' ? 'active' : ''}`}
          onClick={() => setActiveTab('server')}
        >
          ⚡ Server-side Table (React Query + Workspace DB)
        </button>
        <button
          className={`tab-btn ${activeTab === 'client' ? 'active' : ''}`}
          onClick={() => setActiveTab('client')}
        >
          💻 Client-side Table (In-Memory + Custom Filtering)
        </button>
      </div>

      {activeTab === 'server' ? (
        <div>
          <DataTable
            columns={serverColumns}
            data={serverDocResponse?.items ?? []}
            title="Server-side Workspace Documents Table"
            subtitle="Demonstrates Server-side Pagination, Sorting, Search Filtering & React Query state caching."
            isLoading={isServerLoading}
            isServerSide={true}
            pageCount={serverDocResponse?.total_pages ?? 1}
            pagination={serverPagination}
            onPaginationChange={setServerPagination}
            sorting={serverSorting}
            onSortingChange={setServerSorting}
            globalFilter={serverGlobalFilter}
            onGlobalFilterChange={setServerGlobalFilter}
            onDeleteSelectedRows={handleDeleteServerRows}
          />
        </div>
      ) : (
        <div>
          <DataTable
            columns={clientColumns}
            data={clientData}
            title="Client-side Study Materials Table"
            subtitle="Demonstrates instant multi-column sorting, column filters, global search, and row selection."
            onDeleteSelectedRows={handleDeleteClientRows}
          />
        </div>
      )}
    </div>
  );
}

export default TableDemo;
