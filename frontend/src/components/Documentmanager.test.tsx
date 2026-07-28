import { describe, it, expect } from 'vitest';
import { render, screen, userEvent, fireEvent } from '../test/test-utils';
import { DocumentManager } from './Documentmanager';

describe('DocumentManager Component', () => {
  it('renders section title, file input label, and upload button', () => {
    render(<DocumentManager />);

    expect(screen.getByRole('heading', { level: 3, name: /document manager/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/upload pdf study guide/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload file/i })).toBeInTheDocument();
  });

  it('rejects non-PDF file upload and shows validation error alert', () => {
    render(<DocumentManager />);

    const fileInput = screen.getByLabelText(/upload pdf study guide/i);
    const txtFile = new File(['hello world'], 'notes.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, { target: { files: [txtFile] } });

    const alertBox = screen.getByRole('alert');
    expect(alertBox).toBeInTheDocument();
    expect(alertBox).toHaveTextContent(/only pdf documents are supported\./i);
  });

  it('enables upload button when a valid PDF file is selected', async () => {
    const user = userEvent.setup();
    render(<DocumentManager />);

    const uploadBtn = screen.getByRole('button', { name: /upload file/i });
    expect(uploadBtn).toBeDisabled();

    const fileInput = screen.getByLabelText(/upload pdf study guide/i);
    const pdfFile = new File(['%PDF-1.4 mock content'], 'study-guide.pdf', { type: 'application/pdf' });

    await user.upload(fileInput, pdfFile);

    expect(uploadBtn).toBeEnabled();
  });
});