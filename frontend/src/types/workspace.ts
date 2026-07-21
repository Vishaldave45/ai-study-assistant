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
export interface WorkspaceDetails {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceDetail extends WorkspaceDetails {}

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
export interface WorkSpaceListResponse {
  items: WorkspaceSummary[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
