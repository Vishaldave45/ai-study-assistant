import { describe, it, expect } from 'vitest';
import { render, screen, userEvent } from '../../test/test-utils';
import { Sidebar } from './Sidebar';

describe('Sidebar Component', () => {
  it('renders sidebar navigation landmarks and workspace header', () => {
    render(<Sidebar />);

    const asideNav = screen.getByRole('complementary', { name: /sidebar navigation/i });
    const workspaceHeading = screen.getByRole('heading', { level: 4, name: /workspaces/i });
    const addWorkspaceBtn = screen.getByRole('button', { name: /create new workspace/i });
    const logoutBtn = screen.getByRole('button', { name: /log out/i });

    expect(asideNav).toBeInTheDocument();
    expect(workspaceHeading).toBeInTheDocument();
    expect(addWorkspaceBtn).toBeInTheDocument();
    expect(logoutBtn).toBeInTheDocument();
  });

  it('renders empty state text when no workspaces exist', () => {
    render(<Sidebar />);

    expect(screen.getByText(/no workspaces found\./i)).toBeInTheDocument();
  });

  it('opens workspace creation modal when "+ Add" button is clicked', async () => {
    const user = userEvent.setup();
    render(<Sidebar />);

    const addButton = screen.getByRole('button', { name: /create new workspace/i });
    await user.click(addButton);

    expect(screen.getByRole('heading', { level: 3, name: /create workspace/i })).toBeInTheDocument();
  });
});
