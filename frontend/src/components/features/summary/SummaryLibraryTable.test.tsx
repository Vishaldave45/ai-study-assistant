import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../../../test/test-utils';
import { SummaryLibraryTable } from './SummaryLibraryTable';
import type { SavedSummary } from '../../../types/summary';

const mockSummaries: SavedSummary[] = [
  {
    id: 'sum-1',
    workspace_id: 'ws-1',
    document_name: 'Physics_Notes.pdf',
    template_type: 'short',
    title: 'Physics Summary',
    summary: 'Quantum mechanics overview notes.',
    chunk_count: 3,
    processing_time_ms: 1200,
    model: 'gemini-2.5-flash',
    created_at: '2026-07-29T10:00:00Z',
  },
];

describe('SummaryLibraryTable Component', () => {
  it('renders summary title, document source, and format badge', () => {
    const handleDeleteSingle = vi.fn();
    const handleDeleteMultiple = vi.fn();

    render(
      <SummaryLibraryTable
        summaries={mockSummaries}
        onDeleteSummary={handleDeleteSingle}
        onDeleteSummaries={handleDeleteMultiple}
      />
    );

    expect(screen.getByText(/physics summary/i)).toBeInTheDocument();
    expect(screen.getByText(/physics_notes\.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/short/i)).toBeInTheDocument();
  });

  it('opens summary booklet modal when title is clicked', async () => {
    const user = userEvent.setup();
    const handleDeleteSingle = vi.fn();
    const handleDeleteMultiple = vi.fn();

    render(
      <SummaryLibraryTable
        summaries={mockSummaries}
        onDeleteSummary={handleDeleteSingle}
        onDeleteSummaries={handleDeleteMultiple}
      />
    );

    const titleElement = screen.getByText(/physics summary/i);
    await user.click(titleElement);

    expect(screen.getByRole('heading', { level: 3, name: /physics summary/i })).toBeInTheDocument();
    expect(screen.getByText(/quantum mechanics overview notes\./i)).toBeInTheDocument();
  });

  it('triggers onDeleteSummary when delete button is clicked', async () => {
    const user = userEvent.setup();
    const handleDeleteSingle = vi.fn();
    const handleDeleteMultiple = vi.fn();

    render(
      <SummaryLibraryTable
        summaries={mockSummaries}
        onDeleteSummary={handleDeleteSingle}
        onDeleteSummaries={handleDeleteMultiple}
      />
    );

    const deleteBtn = screen.getByRole('button', { name: '🗑️' });
    await user.click(deleteBtn);

    expect(handleDeleteSingle).toHaveBeenCalledTimes(1);
    expect(handleDeleteSingle).toHaveBeenCalledWith('sum-1');
  });
});
