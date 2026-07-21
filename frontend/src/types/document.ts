/**
 * Document processing status constants.
 */
export const DocumentStatus = {
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  READY: 'ready',
  FAILED: 'failed',
  EMBEDDING: 'embedding',
  EMBEDDED: 'embedded',
} as const;

export type DocumentStatus = typeof DocumentStatus[keyof typeof DocumentStatus];

/**
 * Interface representing a document entity in a workspace.
 */
export interface DocumentItem {
  id: string;
  workspace_id: string;
  original_filename: string;
  stored_filename: string;
  mime_type: string;
  file_size: number;
  page_count: number | null;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
}

/**
 * Paginated list container response returned by document endpoints.
 */
export interface DocumentListResponse {
  items: DocumentItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
