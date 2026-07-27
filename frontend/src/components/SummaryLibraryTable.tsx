import { useState, useMemo } from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from './DataTable/DataTable';
import { SummaryBookletModal } from './SummaryBookletModal';
import type { SavedSummary } from '../types/summary';

interface SummaryLibraryTableProps {
  summaries: SavedSummary[];
  onDeleteSummary: (id: string) => void;
  onDeleteSummaries: (ids: string[]) => void;
}

export function SummaryLibraryTable({
  summaries,
  onDeleteSummary,
  onDeleteSummaries,
}: SummaryLibraryTableProps) {
  const [activeModalSummary, setActiveModalSummary] = useState<SavedSummary | null>(null);
  const [selectedBookletSummaries, setSelectedBookletSummaries] = useState<SavedSummary[] | null>(null);

  // TanStack Table Column Definitions
  const columns = useMemo<ColumnDef<SavedSummary>[]>(
    () => [
      {
        accessorKey: 'title',
        header: 'Summary Title',
        cell: (info: any) => {
          const row = info.row.original as SavedSummary;
          return (
            <div
              style={{ fontWeight: 600, color: '#0066cc', cursor: 'pointer' }}
              onClick={() => setActiveModalSummary(row)}
              title="Click to view full summary"
            >
              📝 {info.getValue()}
            </div>
          );
        },
      },
      {
        accessorKey: 'document_name',
        header: 'Material Source',
        cell: (info: any) => (
          <span style={{ fontSize: '0.88rem', color: '#475569' }}>
            📄 {info.getValue()}
          </span>
        ),
      },
      {
        accessorKey: 'template_type',
        header: 'Format',
        cell: (info: any) => {
          const tmpl = info.getValue() as string;
          const label =
            tmpl === 'short'
              ? 'Short'
              : tmpl === 'detailed'
              ? 'Detailed'
              : tmpl === 'bullet'
              ? 'Bullets'
              : tmpl === 'revision_notes'
              ? 'Revision Notes'
              : 'Key Takeaways';
          const colorClass =
            tmpl === 'revision_notes'
              ? 'purple'
              : tmpl === 'detailed'
              ? 'blue'
              : tmpl === 'key_takeaways'
              ? 'orange'
              : 'green';
          return <span className={`status-pill ${colorClass}`}>{label}</span>;
        },
      },
      {
        accessorKey: 'chunk_count',
        header: 'Chunks & Speed',
        cell: (info: any) => {
          const row = info.row.original as SavedSummary;
          const speedSec = (row.processing_time_ms / 1000).toFixed(1);
          return (
            <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
              📦 {row.chunk_count} chunks ({speedSec}s)
            </span>
          );
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Generated Date',
        cell: (info: any) => new Date(info.getValue()).toLocaleDateString(),
      },
      {
        id: 'actions',
        header: 'Actions',
        enableSorting: false,
        enableColumnFilter: false,
        cell: (info: any) => {
          const row = info.row.original as SavedSummary;
          return (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setActiveModalSummary(row)}
                title="Inspect Summary"
                style={{
                  background: '#f1f5f9',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  cursor: 'pointer',
                  fontSize: '0.82rem',
                }}
              >
                👁️ View
              </button>
              <button
                onClick={() => onDeleteSummary(row.id)}
                title="Delete Summary"
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1em' }}
              >
                🗑️
              </button>
            </div>
          );
        },
      },
    ],
    [onDeleteSummary]
  );

  const handleDeleteSelected = (selectedRows: SavedSummary[]) => {
    const ids = selectedRows.map((r) => r.id);
    onDeleteSummaries(ids);
  };

  return (
    <div style={{ marginTop: '15px' }}>
      {/* TanStack Table Instance */}
      <DataTable
        columns={columns}
        data={summaries}
        title="Saved AI Study Summaries"
        subtitle="Search, filter by format, sort by date, and select multiple summaries to compile a Master Revision Booklet."
        onDeleteSelectedRows={handleDeleteSelected}
      />

      {/* Export Booklet Trigger Banner if rows selected */}
      {summaries.length > 0 && (
        <div
          style={{
            marginTop: '15px',
            padding: '16px',
            background: '#f0f9ff',
            border: '1px solid #bae6fd',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <strong style={{ color: '#0369a1', fontSize: '0.95rem' }}>
              📚 Compile Master Study Booklet
            </strong>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#0284c7' }}>
              Export all saved summaries in this workspace into a single organized Markdown booklet.
            </p>
          </div>
          <button
            onClick={() => setSelectedBookletSummaries(summaries)}
            style={{
              padding: '8px 16px',
              background: '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.88rem',
            }}
          >
            📚 Export All ({summaries.length}) to Booklet
          </button>
        </div>
      )}

      {/* Inspect Single Summary Modal */}
      {activeModalSummary && (
        <SummaryBookletModal
          isOpen={!!activeModalSummary}
          onClose={() => setActiveModalSummary(null)}
          mode="single"
          summary={activeModalSummary}
        />
      )}

      {/* Master Booklet Modal */}
      {selectedBookletSummaries && (
        <SummaryBookletModal
          isOpen={!!selectedBookletSummaries}
          onClose={() => setSelectedBookletSummaries(null)}
          mode="booklet"
          selectedSummaries={selectedBookletSummaries}
        />
      )}
    </div>
  );
}
