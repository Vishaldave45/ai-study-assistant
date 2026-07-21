import apiClient from './client';
import type { DocumentItem, DocumentListResponse } from '../types/document.ts';
import type { MessageResponse } from '../types/auth';

/**
 * Document API methods wrapper.
 */
export const documentApi = {
  /**
   * Fetches a paginated list of documents inside a workspace.
   */
  list: async (
    workspaceId: string,
    params?: { page?: number; page_size?: number; query?: string }
  ): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/documents', {
      params: { ...params, workspace_id: workspaceId },
    });
    return response.data;
  },

  /**
   * Fetches detailed information/metadata for a specific document.
   */
  get: async (id: string): Promise<DocumentItem> => {
    const response = await apiClient.get<DocumentItem>(`/documents/${id}`);
    return response.data;
  },

  /**
   * Uploads a document to a workspace using multipart/form-data.
   */
  upload: async (workspaceId: string, file: File): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('workspace_id', workspaceId);
    formData.append('file', file);

    const response = await apiClient.post<DocumentItem>('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Deletes a document record and its physical storage file.
   */
  delete: async (id: string): Promise<MessageResponse> => {
    const response = await apiClient.delete<MessageResponse>(`/documents/${id}`);
    return response.data;
  },
};
export default documentApi;
