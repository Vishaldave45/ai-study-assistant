import type { Table } from '@tanstack/react-table';

interface DataTablePaginationProps<TData> {
  table: Table<TData>;
  pageSizeOptions?: number[];
}

export function DataTablePagination<TData>({
  table,
  pageSizeOptions = [5, 10, 20, 50],
}: DataTablePaginationProps<TData>) {
  const { pageIndex, pageSize } = table.getState().pagination;
  const pageCount = table.getPageCount();
  const totalRows = table.getFilteredRowModel().rows.length;

  return (
    <div className="data-table-pagination">
      <div className="data-table-rows-per-page">
        <label htmlFor="rows-per-page-select">Rows per page:</label>
        <select
          id="rows-per-page-select"
          value={pageSize}
          onChange={(e) => {
            table.setPageSize(Number(e.target.value));
          }}
          className="data-table-select"
        >
          {pageSizeOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      <div className="data-table-pagination-info">
        Page <strong>{pageCount === 0 ? 0 : pageIndex + 1}</strong> of{' '}
        <strong>{pageCount}</strong> ({totalRows} items)
      </div>

      <div className="data-table-pagination-nav">
        <button
          onClick={() => table.setPageIndex(0)}
          disabled={!table.getCanPreviousPage()}
          className="pagination-btn"
          title="First Page"
        >
          ⏮ First
        </button>
        <button
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
          className="pagination-btn"
          title="Previous Page"
        >
          ◀ Prev
        </button>
        <button
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
          className="pagination-btn"
          title="Next Page"
        >
          Next ▶
        </button>
        <button
          onClick={() => table.setPageIndex(pageCount - 1)}
          disabled={!table.getCanNextPage()}
          className="pagination-btn"
          title="Last Page"
        >
          Last ⏭
        </button>
      </div>
    </div>
  );
}
