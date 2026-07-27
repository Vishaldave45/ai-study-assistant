import { useState, useEffect, useMemo } from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from './DataTable/DataTable';
import { useWorkspace } from '../hooks/useWorkspace';
import { usageTracker } from '../utils/usageTracker';
import type { AiUsageRecord } from '../types/usage';

export function AiUsageTable() {
  const { activeWorkspace } = useWorkspace();
  const [logs, setLogs] = useState<AiUsageRecord[]>([]);

  // Load usage logs
  useEffect(() => {
    if (activeWorkspace) {
      const workspaceLogs = usageTracker.getLogs(activeWorkspace.id);
      setLogs(workspaceLogs);
    } else {
      setLogs(usageTracker.getLogs());
    }
  }, [activeWorkspace]);

  // Compute KPI Metrics
  const metrics = useMemo(() => {
    const totalCalls = logs.length;
    const totalTokens = logs.reduce((sum, item) => sum + item.total_tokens, 0);
    const totalCost = logs.reduce((sum, item) => sum + item.estimated_cost, 0);
    const avgLatencyMs =
      totalCalls > 0
        ? logs.reduce((sum, item) => sum + item.processing_time_ms, 0) / totalCalls
        : 0;

    return {
      totalCalls,
      totalTokens,
      totalCost,
      avgLatencySec: (avgLatencyMs / 1000).toFixed(2),
    };
  }, [logs]);

  // TanStack Table Columns
  const columns = useMemo<ColumnDef<AiUsageRecord>[]>(
    () => [
      {
        accessorKey: 'feature',
        header: 'Feature / Endpoint',
        cell: (info: any) => {
          const feat = info.getValue() as string;
          const colorClass =
            feat === 'RAG Chat'
              ? 'blue'
              : feat === 'AI Summarizer'
              ? 'purple'
              : feat === 'Title Generator'
              ? 'orange'
              : 'green';
          return <span className={`status-pill ${colorClass}`}>{feat}</span>;
        },
      },
      {
        accessorKey: 'model',
        header: 'AI Model',
        cell: (info: any) => (
          <code style={{ fontSize: '0.85rem', color: '#0066cc' }}>{info.getValue()}</code>
        ),
      },
      {
        accessorKey: 'prompt_tokens',
        header: 'Prompt Tokens',
        cell: (info: any) => info.getValue().toLocaleString(),
      },
      {
        accessorKey: 'completion_tokens',
        header: 'Completion Tokens',
        cell: (info: any) => info.getValue().toLocaleString(),
      },
      {
        accessorKey: 'total_tokens',
        header: 'Total Tokens',
        cell: (info: any) => (
          <strong style={{ color: '#0f172a' }}>{info.getValue().toLocaleString()}</strong>
        ),
      },
      {
        accessorKey: 'estimated_cost',
        header: 'Est. Cost ($)',
        cell: (info: any) => {
          const cost = info.getValue() as number;
          return (
            <span style={{ fontFamily: 'monospace', fontWeight: 600, color: '#15803d' }}>
              ${cost.toFixed(6)}
            </span>
          );
        },
      },
      {
        accessorKey: 'processing_time_ms',
        header: 'Latency',
        cell: (info: any) => {
          const ms = info.getValue() as number;
          return `${(ms / 1000).toFixed(2)}s`;
        },
      },
      {
        accessorKey: 'timestamp',
        header: 'Date & Time',
        cell: (info: any) => new Date(info.getValue()).toLocaleString(),
      },
    ],
    []
  );

  const handleDeleteSelected = (selectedRows: AiUsageRecord[]) => {
    const ids = selectedRows.map((r) => r.id);
    const updated = usageTracker.deleteLogs(ids);
    setLogs(activeWorkspace ? updated.filter((l) => l.workspace_id === activeWorkspace.id) : updated);
  };

  const handleClearAll = () => {
    usageTracker.clearAll();
    setLogs([]);
  };

  return (
    <div style={{ marginTop: '10px' }}>
      {/* Top KPI Summary Metrics Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <div className="kpi-card shadow-sm">
          <span className="kpi-icon">📊</span>
          <div className="kpi-content">
            <span className="kpi-label">Total AI Queries</span>
            <span className="kpi-value">{metrics.totalCalls}</span>
          </div>
        </div>

        <div className="kpi-card shadow-sm">
          <span className="kpi-icon">🔢</span>
          <div className="kpi-content">
            <span className="kpi-label">Total Tokens Used</span>
            <span className="kpi-value">{metrics.totalTokens.toLocaleString()}</span>
          </div>
        </div>

        <div className="kpi-card shadow-sm">
          <span className="kpi-icon">💰</span>
          <div className="kpi-content">
            <span className="kpi-label">Total Estimated Cost</span>
            <span className="kpi-value" style={{ color: '#15803d' }}>
              ${metrics.totalCost.toFixed(5)}
            </span>
          </div>
        </div>

        <div className="kpi-card shadow-sm">
          <span className="kpi-icon">⚡</span>
          <div className="kpi-content">
            <span className="kpi-label">Avg Latency Speed</span>
            <span className="kpi-value">{metrics.avgLatencySec}s</span>
          </div>
        </div>
      </div>

      {/* TanStack Table View */}
      <DataTable
        columns={columns}
        data={logs}
        title="AI API & Token Consumption Logs"
        subtitle="Track real-time token usage, latency, and estimated Gemini API costs for your active workspace."
        onDeleteSelectedRows={handleDeleteSelected}
      />

      {logs.length > 0 && (
        <div style={{ marginTop: '15px', textAlign: 'right' }}>
          <button
            onClick={handleClearAll}
            style={{
              padding: '6px 12px',
              background: '#fee2e2',
              color: '#b91c1c',
              border: '1px solid #fca5a5',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 600,
            }}
          >
            🗑️ Clear All Usage Logs
          </button>
        </div>
      )}
    </div>
  );
}

export default AiUsageTable;
