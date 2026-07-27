import { useState, useEffect } from 'react';
import axios from 'axios';
import { useWorkspace } from '../hooks/useWorkspace';
import { useDocument } from '../hooks/useDocument';
import { summaryApi } from '../api/summary';
import { summaryStorage } from '../utils/summaryStorage';
import { SummaryLibraryTable } from './SummaryLibraryTable';
import type { SummaryTemplateType, SummaryResponse, SavedSummary } from '../types/summary';

interface TemplateOption {
  type: SummaryTemplateType;
  label: string;
  icon: string;
  description: string;
}

const TEMPLATE_OPTIONS: TemplateOption[] = [
  {
    type: 'short',
    label: 'Short Summary',
    icon: '⚡',
    description: 'Concise 1-2 paragraph overview of core themes.',
  },
  {
    type: 'detailed',
    label: 'Detailed Summary',
    icon: '📖',
    description: 'Comprehensive analysis with logical headings and depth.',
  },
  {
    type: 'bullet',
    label: 'Bullet Points',
    icon: '📌',
    description: 'Structured bullet highlights of primary findings.',
  },
  {
    type: 'revision_notes',
    label: 'Revision Notes',
    icon: '📝',
    description: 'Key terminology, concept breakdowns, and study tips.',
  },
  {
    type: 'key_takeaways',
    label: 'Key Takeaways',
    icon: '💡',
    description: 'Most critical takeaways and practical lessons.',
  },
];

export function SummaryGenerator() {
  const { activeWorkspace } = useWorkspace();
  const { documents } = useDocument();

  const [subTab, setSubTab] = useState<'generator' | 'library'>('generator');
  const [selectedDocId, setSelectedDocId] = useState<string>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<SummaryTemplateType>('short');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [summaryData, setSummaryData] = useState<SummaryResponse | null>(null);
  const [savedSummaries, setSavedSummaries] = useState<SavedSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Load saved summaries for active workspace
  useEffect(() => {
    if (activeWorkspace) {
      const items = summaryStorage.getSummaries(activeWorkspace.id);
      setSavedSummaries(items);
    } else {
      setSavedSummaries([]);
    }
  }, [activeWorkspace]);

  const getErrorMessage = (err: unknown): string => {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data;
      if (data && typeof data === 'object' && 'detail' in data) {
        return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
      return err.message;
    }
    if (err instanceof Error) return err.message;
    return 'Failed to generate study summary.';
  };

  const handleGenerate = async () => {
    if (!activeWorkspace) return;

    setIsGenerating(true);
    setError(null);
    setCopied(false);

    try {
      const res = await summaryApi.generate({
        workspace_id: activeWorkspace.id,
        document_id: selectedDocId === 'all' ? null : selectedDocId,
        template_type: selectedTemplate,
      });
      setSummaryData(res);

      // Auto-save to workspace summary library
      const docName =
        selectedDocId === 'all'
          ? 'Entire Workspace'
          : documents.find((d) => d.id === selectedDocId)?.original_filename || 'Document';

      const templateLabel =
        TEMPLATE_OPTIONS.find((t) => t.type === selectedTemplate)?.label || 'Summary';

      const newSavedItem: SavedSummary = {
        ...res,
        id: `sum_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
        title: `${templateLabel} (${docName})`,
        workspace_id: activeWorkspace.id,
        document_name: docName,
        template_type: selectedTemplate,
        created_at: new Date().toISOString(),
      };

      const updatedList = summaryStorage.saveSummary(activeWorkspace.id, newSavedItem);
      setSavedSummaries(updatedList);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteSingleSummary = (id: string) => {
    if (!activeWorkspace) return;
    const updated = summaryStorage.deleteSummary(activeWorkspace.id, id);
    setSavedSummaries(updated);
  };

  const handleDeleteMultipleSummaries = (ids: string[]) => {
    if (!activeWorkspace) return;
    const updated = summaryStorage.deleteSummaries(activeWorkspace.id, ids);
    setSavedSummaries(updated);
  };

  const handleCopy = () => {
    if (!summaryData?.summary) return;
    navigator.clipboard.writeText(summaryData.summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!activeWorkspace) {
    return (
      <div className="summary-welcome-state">
        <p>Please select a workspace to generate AI study summaries.</p>
      </div>
    );
  }

  return (
    <div className="summary-container">
      {/* Sub-tab navigation */}
      <div className="tab-switcher" style={{ marginBottom: '15px' }}>
        <button
          className={`tab-btn ${subTab === 'generator' ? 'active' : ''}`}
          onClick={() => setSubTab('generator')}
        >
          ✨ Generate New Summary
        </button>
        <button
          className={`tab-btn ${subTab === 'library' ? 'active' : ''}`}
          onClick={() => setSubTab('library')}
        >
          📚 Summaries Library ({savedSummaries.length})
        </button>
      </div>

      {subTab === 'library' ? (
        <SummaryLibraryTable
          summaries={savedSummaries}
          onDeleteSummary={handleDeleteSingleSummary}
          onDeleteSummaries={handleDeleteMultipleSummaries}
        />
      ) : (
        <>
          {/* 1. Header & Controls Card */}
          <div className="summary-card shadow-sm">
        <div className="summary-card-header">
          <h2>📝 AI Summary Generator</h2>
          <p className="summary-subtitle">
            Generate grounded study notes and key takeaways directly from your uploaded materials.
          </p>
        </div>

        {/* Scope Selection */}
        <div className="summary-section">
          <label className="summary-label">Select Material Scope:</label>
          <select
            className="summary-select"
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            disabled={isGenerating}
          >
            <option value="all">📁 Entire Workspace (All Ingested Documents)</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                📄 {doc.original_filename}
              </option>
            ))}
          </select>
        </div>

        {/* Template Format Selector */}
        <div className="summary-section">
          <label className="summary-label">Select Summary Format:</label>
          <div className="template-grid">
            {TEMPLATE_OPTIONS.map((tmpl) => {
              const isSelected = selectedTemplate === tmpl.type;
              return (
                <button
                  key={tmpl.type}
                  type="button"
                  className={`template-pill ${isSelected ? 'active' : ''}`}
                  onClick={() => setSelectedTemplate(tmpl.type)}
                  disabled={isGenerating}
                >
                  <span className="template-icon">{tmpl.icon}</span>
                  <div className="template-info">
                    <span className="template-name">{tmpl.label}</span>
                    <span className="template-desc">{tmpl.description}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Generate Button */}
        <div className="summary-action-bar">
          <button
            className="generate-summary-btn"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <span className="spinner"></span> Generating Summary...
              </>
            ) : (
              <>✨ Generate Study Summary</>
            )}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="summary-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)} className="clear-error-btn">
            ✕
          </button>
        </div>
      )}

      {/* 2. Output Card */}
      {summaryData && (
        <div className="summary-output-card shadow-sm fade-in">
          <div className="output-card-header">
            <div className="output-title-group">
              <h3>Generated Summary</h3>
              <span className="model-badge">✨ {summaryData.model}</span>
            </div>
            <button
              className={`copy-btn ${copied ? 'copied' : ''}`}
              onClick={handleCopy}
              title="Copy to clipboard"
            >
              {copied ? '✓ Copied!' : '📋 Copy Text'}
            </button>
          </div>

          <div className="output-metrics-bar">
            <span>📦 Chunks Used: <strong>{summaryData.chunk_count}</strong></span>
            <span>⚡ Time: <strong>{(summaryData.processing_time_ms / 1000).toFixed(2)}s</strong></span>
            {summaryData.token_usage?.total_tokens && (
              <span>🔢 Tokens: <strong>{summaryData.token_usage.total_tokens}</strong></span>
            )}
          </div>

          <div className="output-body">
            <pre className="summary-text-display">{summaryData.summary}</pre>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
}

export default SummaryGenerator;
