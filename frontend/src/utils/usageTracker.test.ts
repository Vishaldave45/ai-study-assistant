import { describe, it, expect, beforeEach, vi } from 'vitest';
import { usageTracker } from './usageTracker';

describe('usageTracker Utility', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('calculates cost correctly based on token counts and model pricing', () => {
    // Standard LLM model
    const llmCost = usageTracker.calculateCost('gemini-2.5-flash', 1_000_000, 1_000_000);
    expect(llmCost).toBeCloseTo(0.375, 4); // 0.075 + 0.30

    // Embedding model
    const embedCost = usageTracker.calculateCost('bge-m3', 1_000_000, 0);
    expect(embedCost).toBeCloseTo(0.01, 4);
  });

  it('logs an AI usage record to localStorage', () => {
    const record = usageTracker.logUsage(
      'ws-1',
      'RAG Chat',
      'gemini-2.5-flash',
      500,
      150,
      1200,
      'Query test'
    );

    expect(record.workspace_id).toBe('ws-1');
    expect(record.feature).toBe('RAG Chat');
    expect(record.total_tokens).toBe(650);

    const logs = usageTracker.getLogs('ws-1');
    expect(logs).toHaveLength(1);
    expect(logs[0].id).toBe(record.id);
  });

  it('filters logs by workspace ID', () => {
    usageTracker.logUsage('ws-1', 'RAG Chat', 'gemini-2.5-flash', 100, 50, 500);
    usageTracker.logUsage('ws-2', 'AI Summarizer', 'gemini-2.5-flash', 200, 100, 800);

    expect(usageTracker.getLogs()).toHaveLength(2);
    expect(usageTracker.getLogs('ws-1')).toHaveLength(1);
    expect(usageTracker.getLogs('ws-2')).toHaveLength(1);
  });

  it('deletes specific usage log items', () => {
    const r1 = usageTracker.logUsage('ws-1', 'RAG Chat', 'gemini-2.5-flash', 100, 50, 500);
    const r2 = usageTracker.logUsage('ws-1', 'AI Summarizer', 'gemini-2.5-flash', 200, 100, 800);

    const remaining = usageTracker.deleteLogs([r1.id]);
    expect(remaining).toHaveLength(1);
    expect(remaining[0].id).toBe(r2.id);
  });

  it('clears all usage logs when clearAll is called', () => {
    usageTracker.logUsage('ws-1', 'RAG Chat', 'gemini-2.5-flash', 100, 50, 500);
    usageTracker.clearAll();

    expect(usageTracker.getLogs()).toEqual([]);
  });
});
