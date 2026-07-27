import type { SavedSummary } from '../types/summary';

const STORAGE_PREFIX = 'ai_study_summaries_';

export const summaryStorage = {
  /**
   * Retrieves all saved summaries for a given workspace ID.
   */
  getSummaries: (workspaceId: string): SavedSummary[] => {
    try {
      const raw = localStorage.getItem(`${STORAGE_PREFIX}${workspaceId}`);
      if (!raw) return [];
      return JSON.parse(raw) as SavedSummary[];
    } catch (e) {
      console.error('Failed to parse saved summaries from localStorage:', e);
      return [];
    }
  },

  /**
   * Saves a new summary item to the workspace summary library.
   */
  saveSummary: (workspaceId: string, summary: SavedSummary): SavedSummary[] => {
    const existing = summaryStorage.getSummaries(workspaceId);
    const updated = [summary, ...existing];
    try {
      localStorage.setItem(`${STORAGE_PREFIX}${workspaceId}`, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save summary to localStorage:', e);
    }
    return updated;
  },

  /**
   * Deletes a specific summary by ID.
   */
  deleteSummary: (workspaceId: string, summaryId: string): SavedSummary[] => {
    const existing = summaryStorage.getSummaries(workspaceId);
    const updated = existing.filter((item) => item.id !== summaryId);
    try {
      localStorage.setItem(`${STORAGE_PREFIX}${workspaceId}`, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to delete summary from localStorage:', e);
    }
    return updated;
  },

  /**
   * Bulk deletes multiple summaries by IDs.
   */
  deleteSummaries: (workspaceId: string, summaryIds: string[]): SavedSummary[] => {
    const idSet = new Set(summaryIds);
    const existing = summaryStorage.getSummaries(workspaceId);
    const updated = existing.filter((item) => !idSet.has(item.id));
    try {
      localStorage.setItem(`${STORAGE_PREFIX}${workspaceId}`, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to bulk delete summaries from localStorage:', e);
    }
    return updated;
  },
};
