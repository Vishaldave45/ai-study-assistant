import { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table';
import type {
  ColumnDef,
  SortingState,
  ColumnFiltersState,
  PaginationState,
  RowSelectionState,
} from '@tanstack/react-table';
import { DataTableControls } from './DataTableControls';
import { DataTablePagination } from './DataTablePagination';

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  title?: string;
  subtitle?: string;
  emptyMessage?: string;
  isLoading?: boolean;
  
  // Server-side props (optional)
  isServerSide?: boolean;
  pageCount?: number;
  pagination?: PaginationState;
  onPaginationChange?: (pagination: PaginationState) => void;
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  globalFilter?: string;
  onGlobalFilterChange?: (filter: string) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: (filters: ColumnFiltersState) => void;
  
  // Selection callback
  onDeleteSelectedRows?: (selectedRows: TData[]) => void;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  title,
  subtitle,
  emptyMessage,
  isLoading = false,
  isServerSide = false,
  pageCount: serverPageCount,
  pagination: externalPagination,
  onPaginationChange: externalOnPaginationChange,
  sorting: externalSorting,
  onSortingChange: externalOnSortingChange,
  globalFilter: externalGlobalFilter,
  onGlobalFilterChange: externalOnGlobalFilterChange,
  columnFilters: externalColumnFilters,
  onColumnFiltersChange: externalOnColumnFiltersChange,
  onDeleteSelectedRows,
}: DataTableProps<TData, TValue>) {
  // Local state for client-side mode
  const [internalSorting, setInternalSorting] = useState<SortingState>([]);
  const [internalGlobalFilter, setInternalGlobalFilter] = useState<string>('');
  const [internalColumnFilters, setInternalColumnFilters] = useState<ColumnFiltersState>([]);
  const [internalPagination, setInternalPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  // Resolve state & handlers (External for Server-side, Internal for Client-side)
  const sorting = externalSorting ?? internalSorting;
  const setSorting = externalOnSortingChange ?? setInternalSorting;

  const globalFilter = externalGlobalFilter ?? internalGlobalFilter;
  const setGlobalFilter = externalOnGlobalFilterChange ?? setInternalGlobalFilter;

  const columnFilters = externalColumnFilters ?? internalColumnFilters;
  const setColumnFilters = externalOnColumnFiltersChange ?? setInternalColumnFilters;

  const pagination = externalPagination ?? internalPagination;
  const setPagination = externalOnPaginationChange ?? setInternalPagination;

  // Add Row Selection Column to front of columns if selection is enabled
  const tableColumns = useMemo(() => {
    const selectionColumn: ColumnDef<TData, TValue> = {
      id: 'select',
      header: ({ table }: { table: any }) => (
        <input
          type="checkbox"
          checked={table.getIsAllPageRowsSelected()}
          onChange={table.getToggleAllPageRowsSelectedHandler()}
          aria-label="Select all rows"
          className="row-checkbox"
        />
      ),
      cell: ({ row }: { row: any }) => (
        <input
          type="checkbox"
          checked={row.getIsSelected()}
          disabled={!row.getCanSelect()}
          onChange={row.getToggleSelectedHandler()}
          aria-label={`Select row ${row.id}`}
          className="row-checkbox"
        />
      ),
      enableSorting: false,
      enableColumnFilter: false,
    };

    return [selectionColumn, ...columns];
  }, [columns]);

  // Construct TanStack Table instance
  const table = useReactTable({
    data,
    columns: tableColumns,
    pageCount: isServerSide ? serverPageCount : undefined,
    state: {
      sorting,
      globalFilter,
      columnFilters,
      pagination,
      rowSelection,
    },
    manualPagination: isServerSide,
    manualSorting: isServerSide,
    manualFiltering: isServerSide,
    onSortingChange: (updater: any) => {
      const nextState = typeof updater === 'function' ? updater(sorting) : updater;
      setSorting(nextState);
    },
    onGlobalFilterChange: (updater: any) => {
      const nextState = typeof updater === 'function' ? updater(globalFilter) : updater;
      setGlobalFilter(nextState);
    },
    onColumnFiltersChange: (updater: any) => {
      const nextState = typeof updater === 'function' ? updater(columnFilters) : updater;
      setColumnFilters(nextState);
    },
    onPaginationChange: (updater: any) => {
      const nextState = typeof updater === 'function' ? updater(pagination) : updater;
      setPagination(nextState);
    },
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: !isServerSide ? getFilteredRowModel() : undefined,
    getSortedRowModel: !isServerSide ? getSortedRowModel() : undefined,
    getPaginationRowModel: !isServerSide ? getPaginationRowModel() : undefined,
  });

  const handleDeleteSelected = () => {
    if (!onDeleteSelectedRows) return;
    const selectedRowsData = table.getSelectedRowModel().rows.map((row: any) => row.original);
    onDeleteSelectedRows(selectedRowsData);
    table.resetRowSelection();
  };

  return (
    <div className="data-table-container">
      {/* Search & Actions Bar */}
      <DataTableControls
        table={table}
        globalFilter={globalFilter}
        onGlobalFilterChange={setGlobalFilter}
        onDeleteSelected={onDeleteSelectedRows ? handleDeleteSelected : undefined}
        title={title}
        subtitle={subtitle}
      />

      {/* Main Table Structure */}
      <div className="data-table-wrapper">
        {isLoading && (
          <div className="data-table-loading-overlay">
            <div className="spinner"></div>
            <span>Fetching data...</span>
          </div>
        )}

        <table className="data-table">
          <thead>
            {table.getHeaderGroups().map((headerGroup: any) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header: any) => {
                  const canSort = header.column.getCanSort();
                  const isSorted = header.column.getIsSorted();

                  return (
                    <th
                      key={header.id}
                      colSpan={header.colSpan}
                      className={canSort ? 'sortable-header' : ''}
                    >
                      <div
                        className="header-content"
                        onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {canSort && (
                          <span className="sort-indicator">
                            {isSorted === 'asc' ? ' ▲' : isSorted === 'desc' ? ' ▼' : ' ⇅'}
                          </span>
                        )}
                      </div>

                      {/* Column Filters Input */}
                      {header.column.getCanFilter() && (
                        <div className="column-filter-box">
                          <input
                            type="text"
                            value={(header.column.getFilterValue() as string) ?? ''}
                            onChange={(e) => header.column.setFilterValue(e.target.value)}
                            placeholder={`Filter...`}
                            className="column-filter-input"
                            onClick={(e) => e.stopPropagation()}
                          />
                        </div>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={tableColumns.length} className="empty-table-cell">
                  {isLoading ? 'Loading records...' : emptyMessage || 'No matching records found.'}
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row: any) => (
                <tr
                  key={row.id}
                  className={row.getIsSelected() ? 'selected-row' : ''}
                >
                  {row.getVisibleCells().map((cell: any) => (
                    <td key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <DataTablePagination table={table} />
    </div>
  );
}
