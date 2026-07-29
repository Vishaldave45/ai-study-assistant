import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../../test/test-utils';
import { SummaryBookletModal } from './SummaryBookletModal';
import type { SavedSummary } from '../../types/summary';

const mockSummary: SavedSummary = {
  id: 'sum-1',
  workspace_id: 'ws-1',
  document_name: 'Physics_Notes.pdf',
  template_type: 'detailed',
  title: 'Quantum Mechanics Summary',
  summary: 'Quantum mechanics is a fundamental theory in physics.',
  chunk_count: 3,
  processing_time_ms: 1200,
  model: 'gemini-1.5-pro',
  created_at: '2026-01-01T00:00:00Z',
};



describe('SummaryBookletModal Component', () => {
  it('returns null when isOpen prop is false', () => {
    const handleClose = vi.fn();
    render(
      <SummaryBookletModal
        isOpen={false}
        onClose={handleClose}
        mode="single"
        summary={mockSummary}
      />
    );

    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('renders single summary title and summary text when open in single mode', () => {
    const handleClose = vi.fn();
    render(
      <SummaryBookletModal
        isOpen={true}
        onClose={handleClose}
        mode="single"
        summary={mockSummary}
      />
    );

    expect(screen.getByRole('heading', { level: 3, name: /quantum mechanics summary/i })).toBeInTheDocument();
    expect(screen.getByText(/source: physics_notes\.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/quantum mechanics is a fundamental theory in physics\./i)).toBeInTheDocument();
  });

  it('compiles and renders Master Revision Booklet in booklet mode', () => {
    const handleClose = vi.fn();
    render(
      <SummaryBookletModal
        isOpen={true}
        onClose={handleClose}
        mode="booklet"
        selectedSummaries={[mockSummary]}
      />
    );

    expect(screen.getByRole('heading', { level: 3, name: /master study revision booklet/i })).toBeInTheDocument();
    expect(screen.getByText(/table of contents/i)).toBeInTheDocument();
  });

  it('triggers onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(
      <SummaryBookletModal
        isOpen={true}
        onClose={handleClose}
        mode="single"
        summary={mockSummary}
      />
    );

    const closeBtn = screen.getByRole('button', { name: '✕' });
    await user.click(closeBtn);


    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
