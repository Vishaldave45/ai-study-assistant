export interface AiUsageRecord {
  id: string;
  workspace_id: string;
  feature: 'RAG Chat' | 'AI Summarizer' | 'Title Generator' | 'Vector Indexing';
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number; // Cost in USD ($)
  processing_time_ms: number;
  timestamp: string;
  details?: string;
}
