import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentApi } from '../api/document';
import type { DocumentListResponse } from '../types/document.ts';

interface UseServerDocumentsParams {
  workspaceId: string | null;
  page: number;
  pageSize: number;
  query?: string;
}

export function useServerDocumentsQuery({
  workspaceId,
  page,
  pageSize,
  query,
}: UseServerDocumentsParams) {
  const queryClient = useQueryClient();

  const documentsQuery = useQuery<DocumentListResponse>({
    queryKey: ['documents', workspaceId, page, pageSize, query],
    queryFn: async () => {
      if (!workspaceId) {
        return { items: [], page: 1, page_size: pageSize, total: 0, total_pages: 0 };
      }
      return documentApi.list(workspaceId, {
        page,
        page_size: pageSize,
        query: query || undefined,
      });
    },
    enabled: !!workspaceId,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', workspaceId] });
    },
  });

  return {
    ...documentsQuery,
    deleteDocument: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
