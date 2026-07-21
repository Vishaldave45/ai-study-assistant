/**
 * Summary structure of a workspace (used in listing views).
 */
export interface WorkspaceSummary {
  id: string;
  name: string;
  description: string | null;
}

/**
 * Detailed representation of a workspace (includes timestamps).
 */
export interface WorkspaceDetail {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Detailed representation of a workspace (alternative name for API mapping).
 */
export interface WorkspaceDetails extends WorkspaceDetail {}

/**
 * Request payload for creating a new workspace.
 */
export interface WorkspaceCreateRequest {
  name: string;
  description?: string;
}

/**
 * Request payload for updating an existing workspace.
 */
export interface WorkspaceUpdateRequest {
  name?: string;
  description?: string;
}

/**
 * Paginated list container response returned by list endpoints.
 */
export interface WorkspaceListResponse {
  items: WorkspaceSummary[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

/**
 * Paginated list container response (alternative case).
 */
export interface WorkSpaceListResponse extends WorkspaceListResponse {}
