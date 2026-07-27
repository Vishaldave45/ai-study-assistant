import type { Table } from '@tanstack/react-table';

interface DataTableControlsProps<TData> {
  table: Table<TData>;
  globalFilter: string;
  onGlobalFilterChange: (value: string) => void;
  onDeleteSelected?: () => void;
  title?: string;
  subtitle?: string;
}

export function DataTableControls<TData>({
  table,
  globalFilter,
  onGlobalFilterChange,
  onDeleteSelected,
  title,
  subtitle,
}: DataTableControlsProps<TData>) {
  const selectedRows = table.getSelectedRowModel().rows;
  const selectedCount = selectedRows.length;
  const totalCount = table.getPreFilteredRowModel().rows.length;

  return (
    <div className="data-table-controls">
      {(title || subtitle) && (
        <div className="data-table-header-info">
          {title && <h3 className="data-table-title">{title}</h3>}
          {subtitle && <p className="data-table-subtitle">{subtitle}</p>}
        </div>
      )}

      <div className="data-table-toolbar">
        {/* Search Bar */}
        <div className="data-table-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={globalFilter ?? ''}
            onChange={(e) => onGlobalFilterChange(e.target.value)}
            placeholder="Search all columns..."
            className="data-table-search-input"
          />
          {globalFilter && (
            <button
              onClick={() => onGlobalFilterChange('')}
              className="search-clear-btn"
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Selected Rows Action Toolbar */}
        {selectedCount > 0 && (
          <div className="data-table-selection-badge">
            <span>{selectedCount} of {totalCount} row(s) selected</span>
            {onDeleteSelected && (
              <button
                onClick={onDeleteSelected}
                className="data-table-action-btn danger"
              >
                🗑️ Delete Selected ({selectedCount})
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
