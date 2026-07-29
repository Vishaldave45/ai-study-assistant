import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workspaceApi } from '../api/workspace';
import type {
  WorkspaceCreateRequest,
  WorkspaceUpdateRequest,
  WorkSpaceListResponse,
  WorkspaceDetail,
} from '../types/workspace.ts';

export function useWorkspacesQuery(isAuthenticated: boolean, searchQuery?: string) {
  const queryClient = useQueryClient();

  const workspacesQuery = useQuery<WorkSpaceListResponse>({
    queryKey: ['workspaces', searchQuery],
    queryFn: () => workspaceApi.list({ query: searchQuery, page_size: 100 }),
    enabled: isAuthenticated,
  });

  const createMutation = useMutation({
    mutationFn: (data: WorkspaceCreateRequest) => workspaceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: WorkspaceUpdateRequest }) =>
      workspaceApi.update(id, data),
    onSuccess: (updatedWs) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      queryClient.invalidateQueries({ queryKey: ['workspace', updatedWs.id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
    },
  });

  return {
    ...workspacesQuery,
    workspaces: workspacesQuery.data?.items || [],
    createWorkspace: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateWorkspace: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteWorkspace: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}

export function useWorkspaceDetailQuery(workspaceId: string | null) {
  return useQuery<WorkspaceDetail | null>({
    queryKey: ['workspace', workspaceId],
    queryFn: async () => {
      if (!workspaceId) return null;
      return workspaceApi.get(workspaceId);
    },
    enabled: !!workspaceId,
  });
}
