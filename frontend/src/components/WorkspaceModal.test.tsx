import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../test/test-utils';
import { WorkspaceModal } from './WorkspaceModal';
import type { WorkspaceSummary } from '../types/workspace';

const mockWorkspace: WorkspaceSummary = {
  id: 'ws-123',
  name: 'Physics 101',
  description: 'Introductory Mechanics',
  document_count: 5,
  summary_count: 2,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('WorkspaceModal Component', () => {
  it('renders dialog landmark and create mode form inputs', () => {
    const handleClose = vi.fn();
    render(<WorkspaceModal type="create" workspace={null} onClose={handleClose} />);

    expect(screen.getByRole('dialog', { name: /create workspace/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3, name: /create workspace/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/workspace name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('populates existing workspace details when opened in edit mode', () => {
    const handleClose = vi.fn();
    render(<WorkspaceModal type="edit" workspace={mockWorkspace} onClose={handleClose} />);

    expect(screen.getByRole('heading', { level: 3, name: /rename workspace "physics 101"/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/workspace name/i)).toHaveValue('Physics 101');
    expect(screen.getByLabelText(/description/i)).toHaveValue('Introductory Mechanics');
  });

  it('renders confirmation warning message and delete button in delete mode', () => {
    const handleClose = vi.fn();
    render(<WorkspaceModal type="delete" workspace={mockWorkspace} onClose={handleClose} />);

    expect(screen.getByRole('heading', { level: 3, name: /delete workspace/i })).toBeInTheDocument();
    expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
  });

  it('triggers onClose when Cancel button is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(<WorkspaceModal type="create" workspace={null} onClose={handleClose} />);

    const cancelBtn = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
