import type { AiUsageRecord } from '../types/usage';

const USAGE_STORAGE_KEY = 'ai_study_usage_logs';

export const usageTracker = {
  /**
   * Calculate estimated cost ($) based on model rates.
   */
  calculateCost: (
    model: string,
    promptTokens: number,
    completionTokens: number
  ): number => {
    // Check pricing tier by model name
    const isEmbedding = model.includes('bge') || model.includes('embed');
    const promptRate = isEmbedding ? 0.01 : 0.075;
    const completionRate = isEmbedding ? 0.01 : 0.30;

    const promptCost = (promptTokens / 1_000_000) * promptRate;
    const completionCost = (completionTokens / 1_000_000) * completionRate;
    const total = promptCost + completionCost;

    return Math.max(total, 0.000001);
  },

  /**
   * Log an AI call to localStorage.
   */
  logUsage: (
    workspaceId: string,
    feature: 'RAG Chat' | 'AI Summarizer' | 'Title Generator' | 'Vector Indexing',
    model: string,
    promptTokens: number,
    completionTokens: number,
    processingTimeMs: number,
    details?: string
  ): AiUsageRecord => {
    const totalTokens = (promptTokens || 0) + (completionTokens || 0);
    const cost = usageTracker.calculateCost(model, promptTokens || 0, completionTokens || 0);

    const record: AiUsageRecord = {
      id: `use_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
      workspace_id: workspaceId,
      feature,
      model: model || 'gemini-2.5-flash',
      prompt_tokens: promptTokens || 0,
      completion_tokens: completionTokens || 0,
      total_tokens: totalTokens,
      estimated_cost: cost,
      processing_time_ms: processingTimeMs || 0,
      timestamp: new Date().toISOString(),
      details,
    };

    const existing = usageTracker.getLogs();
    const updated = [record, ...existing];

    try {
      localStorage.setItem(USAGE_STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save AI usage log to localStorage:', e);
    }

    return record;
  },

  /**
   * Retrieve all stored AI usage logs.
   */
  getLogs: (workspaceId?: string): AiUsageRecord[] => {
    try {
      const raw = localStorage.getItem(USAGE_STORAGE_KEY);
      if (!raw) return [];
      const logs = JSON.parse(raw) as AiUsageRecord[];
      if (workspaceId) {
        return logs.filter((log) => log.workspace_id === workspaceId);
      }
      return logs;
    } catch (e) {
      console.error('Failed to parse AI usage logs:', e);
      return [];
    }
  },

  /**
   * Delete specific logs by ID.
   */
  deleteLogs: (logIds: string[]): AiUsageRecord[] => {
    const idSet = new Set(logIds);
    const existing = usageTracker.getLogs();
    const updated = existing.filter((item) => !idSet.has(item.id));
    try {
      localStorage.setItem(USAGE_STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to delete usage logs:', e);
    }
    return updated;
  },

  /**
   * Clear all usage logs.
   */
  clearAll: (): void => {
    localStorage.removeItem(USAGE_STORAGE_KEY);
  },
};
