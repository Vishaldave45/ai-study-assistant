import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../../../test/test-utils';
import { Modal } from './Modal';

describe('Modal Component', () => {
  it('does not render content when isOpen is false', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={false} onClose={handleClose} title="Hidden Modal">
        <p>Modal body content</p>
      </Modal>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.queryByText(/modal body content/i)).not.toBeInTheDocument();
  });

  it('renders modal title and children when isOpen is true', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Title">
        <p>Modal body content</p>
      </Modal>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /test title/i })).toBeInTheDocument();
    expect(screen.getByText(/modal body content/i)).toBeInTheDocument();
  });

  it('triggers onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Title">
        <p>Modal body content</p>
      </Modal>
    );

    const closeBtn = screen.getByRole('button', { name: /close modal/i });
    await user.click(closeBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('triggers onClose when backdrop overlay is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Title">
        <p>Modal body content</p>
      </Modal>
    );

    const dialogBackdrop = screen.getByRole('dialog');
    await user.click(dialogBackdrop);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
