import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../../../test/test-utils';
import { DataTable } from './DataTable';
import type { ColumnDef } from '@tanstack/react-table';

interface DocumentRecord {
  id: string;
  name: string;
  category: string;
}

const mockColumns: ColumnDef<DocumentRecord, any>[] = [
  {
    accessorKey: 'name',
    header: 'Document Name',
  },
  {
    accessorKey: 'category',
    header: 'Category',
  },
];

const mockData: DocumentRecord[] = [
  { id: '1', name: 'Physics Notes.pdf', category: 'Physics' },
  { id: '2', name: 'Chemistry Summary.docx', category: 'Chemistry' },
];

describe('DataTable Component', () => {
  it('renders data rows and column headers correctly', () => {
    render(<DataTable columns={mockColumns} data={mockData} title="Study Documents" />);

    expect(screen.getByRole('heading', { level: 3, name: /study documents/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /document name/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /category/i })).toBeInTheDocument();

    expect(screen.getByRole('cell', { name: 'Physics Notes.pdf' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'Chemistry Summary.docx' })).toBeInTheDocument();
  });

  it('filters table rows when user types in global search input', async () => {
    const user = userEvent.setup();
    render(<DataTable columns={mockColumns} data={mockData} />);

    const searchInput = screen.getByPlaceholderText(/search all columns/i);
    await user.type(searchInput, 'Physics');

    expect(screen.getByRole('cell', { name: 'Physics Notes.pdf' })).toBeInTheDocument();
    expect(screen.queryByRole('cell', { name: 'Chemistry Summary.docx' })).not.toBeInTheDocument();
  });

  it('renders loading overlay when isLoading prop is true', () => {
    render(<DataTable columns={mockColumns} data={[]} isLoading={true} />);

    expect(screen.getByText(/fetching data\.\.\./i)).toBeInTheDocument();
  });

  it('renders custom empty message when data array is empty', () => {
    render(<DataTable columns={mockColumns} data={[]} emptyMessage="No study documents available." />);

    expect(screen.getByRole('cell', { name: /no study documents available\./i })).toBeInTheDocument();
  });

  it('handles row selection and triggers delete callback with selected rows', async () => {
    const user = userEvent.setup();
    const handleDelete = vi.fn();

    render(
      <DataTable
        columns={mockColumns}
        data={mockData}
        onDeleteSelectedRows={handleDelete}
      />
    );

    const selectRowZeroCheckbox = screen.getByRole('checkbox', { name: /select row 0/i });
    await user.click(selectRowZeroCheckbox);

    const deleteButton = screen.getByRole('button', { name: /delete selected/i });
    await user.click(deleteButton);

    expect(handleDelete).toHaveBeenCalledTimes(1);
    expect(handleDelete).toHaveBeenCalledWith([mockData[0]]);
  });
});

