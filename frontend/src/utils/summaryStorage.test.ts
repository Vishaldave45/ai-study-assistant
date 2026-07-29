import { describe, it, expect, beforeEach, vi } from 'vitest';
import { summaryStorage } from './summaryStorage';
import type { SavedSummary } from '../types/summary';

const mockSummary: SavedSummary = {
  id: 'sum-101',
  workspace_id: 'ws-test',
  document_name: 'Physics.pdf',
  template_type: 'short',
  title: 'Physics Summary',
  summary: 'Core concepts of physics.',
  chunk_count: 2,
  processing_time_ms: 800,
  model: 'gemini-2.5-flash',
  created_at: '2026-07-29T10:00:00Z',
};

describe('summaryStorage Utility', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('returns an empty array when no summaries are saved', () => {
    const items = summaryStorage.getSummaries('ws-test');
    expect(items).toEqual([]);
  });

  it('saves a new summary item and retrieves it by workspace ID', () => {
    const updated = summaryStorage.saveSummary('ws-test', mockSummary);
    expect(updated).toHaveLength(1);
    expect(updated[0]).toEqual(mockSummary);

    const retrieved = summaryStorage.getSummaries('ws-test');
    expect(retrieved).toHaveLength(1);
    expect(retrieved[0].title).toBe('Physics Summary');
  });

  it('deletes a single summary by ID', () => {
    summaryStorage.saveSummary('ws-test', mockSummary);
    const updated = summaryStorage.deleteSummary('ws-test', 'sum-101');
    expect(updated).toEqual([]);
    expect(summaryStorage.getSummaries('ws-test')).toEqual([]);
  });

  it('bulk deletes multiple summaries by IDs', () => {
    const mockSummary2: SavedSummary = { ...mockSummary, id: 'sum-102', title: 'Summary 2' };
    summaryStorage.saveSummary('ws-test', mockSummary);
    summaryStorage.saveSummary('ws-test', mockSummary2);

    const updated = summaryStorage.deleteSummaries('ws-test', ['sum-101']);
    expect(updated).toHaveLength(1);
    expect(updated[0].id).toBe('sum-102');
  });

  it('handles JSON parsing errors gracefully and returns empty array', () => {
    localStorage.setItem('ai_study_summaries_ws-invalid', 'INVALID_JSON{');
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const items = summaryStorage.getSummaries('ws-invalid');
    expect(items).toEqual([]);
    expect(consoleSpy).toHaveBeenCalled();
  });
});
