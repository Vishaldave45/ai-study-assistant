export type SummaryTemplateType = 
  | 'short'
  | 'detailed'
  | 'bullet'
  | 'revision_notes'
  | 'key_takeaways';

export interface SummaryRequest {
  workspace_id: string;
  document_id?: string | null;
  template_type: SummaryTemplateType;
}

export interface SummaryResponse {
  summary: string;
  token_usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  } | null;
  chunk_count: number;
  processing_time_ms: number;
  model: string;
}
