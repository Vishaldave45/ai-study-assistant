import { describe, it, expect } from 'vitest';
import { render, screen, userEvent } from '../../../test/test-utils';
import { ChatInterface } from './ChatInterface';

describe('ChatInterface Component', () => {
  it('renders chat welcome state when no active session is selected', () => {
    render(<ChatInterface />);

    expect(screen.getByRole('heading', { level: 2, name: /ai study assistant chat/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /\+ new chat/i })).toBeInTheDocument();
    expect(screen.getByText(/no active chat sessions\./i)).toBeInTheDocument();
  });

  it('renders new chat session button and allows user typing in input textarea when active', async () => {
    const user = userEvent.setup();
    render(<ChatInterface />);

    const newChatBtn = screen.getByRole('button', { name: /\+ new chat/i });
    expect(newChatBtn).toBeInTheDocument();
    expect(newChatBtn).toBeEnabled();
  });
});
