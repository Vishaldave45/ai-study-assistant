import { useState, memo } from 'react';
import type { SavedSummary } from '../../types/summary';

interface SummaryBookletModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'single' | 'booklet';
  summary?: SavedSummary | null;
  selectedSummaries?: SavedSummary[];
}

export const SummaryBookletModal = memo(function SummaryBookletModal({
  isOpen,
  onClose,
  mode,
  summary,
  selectedSummaries = [],
}: SummaryBookletModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  // Build Master Revision Booklet Markdown content
  const compileBookletMarkdown = (): string => {
    if (mode === 'single' && summary) {
      return summary.summary;
    }

    const now = new Date().toLocaleDateString();
    let booklet = `# 📚 Master Study Revision Booklet\n`;
    booklet += `*Compiled on ${now} • Total Sections: ${selectedSummaries.length}*\n\n`;
    booklet += `---\n\n## 📑 Table of Contents\n\n`;

    selectedSummaries.forEach((item, index) => {
      booklet += `${index + 1}. **${item.title}** (*${item.document_name}* - ${item.template_type})\n`;
    });

    booklet += `\n=========================================\n\n`;

    selectedSummaries.forEach((item, index) => {
      booklet += `### Section ${index + 1}: ${item.title}\n`;
      booklet += `> **Source Document:** ${item.document_name} | **Template:** ${item.template_type} | **Date:** ${new Date(item.created_at).toLocaleDateString()}\n\n`;
      booklet += `${item.summary}\n\n`;
      booklet += `---\n\n`;
    });

    return booklet;
  };

  const bookletText = compileBookletMarkdown();

  const handleCopy = () => {
    navigator.clipboard.writeText(bookletText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const filename =
      mode === 'single' && summary
        ? `${summary.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_summary.md`
        : `Master_Revision_Booklet_${new Date().toISOString().slice(0, 10)}.md`;

    const blob = new Blob([bookletText], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="summary-modal-card shadow-lg" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h3>
              {mode === 'single'
                ? summary?.title || 'Summary Details'
                : `📚 Master Study Revision Booklet (${selectedSummaries.length} Summaries)`}
            </h3>
            {mode === 'single' && summary && (
              <p className="modal-subtitle">
                📄 Source: {summary.document_name} • Format: {summary.template_type}
              </p>
            )}
          </div>
          <button onClick={onClose} className="modal-close-btn" title="Close">
            ✕
          </button>
        </div>

        {/* Toolbar Actions */}
        <div className="modal-toolbar">
          <button
            onClick={handleCopy}
            className={`modal-btn ${copied ? 'success' : 'primary'}`}
          >
            {copied ? '✓ Copied to Clipboard!' : '📋 Copy Text'}
          </button>

          <button onClick={handleDownload} className="modal-btn secondary">
            📥 Download Markdown (.md)
          </button>
        </div>

        {/* Content Body */}
        <div className="modal-body">
          <pre className="modal-text-content">{bookletText}</pre>
        </div>
      </div>
    </div>
  );
});

export default SummaryBookletModal;
