import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '../../../test/test-utils';
import { AiUsageTable } from './AiUsageTable';
import { usageTracker } from '../../../utils/usageTracker';

describe('AiUsageTable Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders KPI metric titles and headers correctly', () => {
    render(<AiUsageTable />);

    expect(screen.getByText(/total ai queries/i)).toBeInTheDocument();
    expect(screen.getByText(/total tokens used/i)).toBeInTheDocument();
    expect(screen.getByText(/total estimated cost/i)).toBeInTheDocument();
    expect(screen.getByText(/avg latency speed/i)).toBeInTheDocument();
  });

  it('renders usage log rows when data exists in storage', () => {
    usageTracker.logUsage(
      'ws-123',
      'RAG Chat',
      'gemini-2.5-flash',
      120,
      40,
      1500,
      'Test query'
    );

    render(<AiUsageTable />);

    expect(screen.getByRole('cell', { name: 'RAG Chat' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'gemini-2.5-flash' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: '160' })).toBeInTheDocument();
  });

  it('displays clear button when logs exist and clears logs on click', async () => {
    const { userEvent } = await import('../../../test/test-utils');
    const user = userEvent.setup();

    usageTracker.logUsage('ws-123', 'RAG Chat', 'gemini-2.5-flash', 100, 50, 800);

    render(<AiUsageTable />);

    const clearBtn = screen.getByRole('button', { name: /clear all usage logs/i });
    expect(clearBtn).toBeInTheDocument();

    await user.click(clearBtn);

    expect(screen.queryByRole('button', { name: /clear all usage logs/i })).not.toBeInTheDocument();
  });
});
