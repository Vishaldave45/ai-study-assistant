import { createContext, useState, useEffect, useMemo, useCallback } from 'react';
import type { ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { workspaceApi } from '../api/workspace';
import { useAuth } from '../hooks/useAuth';
import { useWorkspacesQuery } from '../hooks/useWorkspacesQuery';
import type {
  WorkspaceSummary,
  WorkspaceDetail,
  WorkspaceCreateRequest,
  WorkspaceUpdateRequest,
} from '../types/workspace.ts';

interface WorkspaceContextType {
  workspaces: WorkspaceSummary[];
  activeWorkspace: WorkspaceDetail | null;
  isLoading: boolean;
  error: string | null;
  fetchWorkspaces: (query?: string) => Promise<void>;
  selectWorkspace: (id: string | null) => Promise<void>;
  createWorkspace: (data: WorkspaceCreateRequest) => Promise<WorkspaceDetail>;
  updateWorkspace: (id: string, data: WorkspaceUpdateRequest) => Promise<WorkspaceDetail>;
  deleteWorkspace: (id: string) => Promise<void>;
  clearError: () => void;
}

export const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

const ACTIVE_WORKSPACE_ID_KEY = 'ai_study_active_workspace_id';

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceDetail | null>(null);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(
    () => localStorage.getItem(ACTIVE_WORKSPACE_ID_KEY)
  );
  const [searchQuery, setSearchQuery] = useState<string | undefined>(undefined);
  const [customError, setCustomError] = useState<string | null>(null);

  const {
    workspaces,
    isLoading: isListLoading,
    error: listError,
    createWorkspace: createWsMutation,
    updateWorkspace: updateWsMutation,
    deleteWorkspace: deleteWsMutation,
  } = useWorkspacesQuery(isAuthenticated, searchQuery);

  const clearError = useCallback(() => setCustomError(null), []);

  const getErrorMessage = (err: unknown, defaultMsg: string): string => {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data;
      if (data && typeof data === 'object' && 'detail' in data) {
        return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
      return err.message;
    }
    if (err instanceof Error) {
      return err.message;
    }
    return defaultMsg;
  };

  const fetchWorkspaces = useCallback(async (query?: string) => {
    setSearchQuery(query);
    await queryClient.invalidateQueries({ queryKey: ['workspaces'] });
  }, [queryClient]);

  const selectWorkspace = useCallback(async (id: string | null) => {
    if (!id) {
      setActiveWorkspace(null);
      setActiveWorkspaceId(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      return;
    }

    try {
      setCustomError(null);
      const details = await queryClient.fetchQuery({
        queryKey: ['workspace', id],
        queryFn: () => workspaceApi.get(id),
      });
      setActiveWorkspace(details);
      setActiveWorkspaceId(id);
      localStorage.setItem(ACTIVE_WORKSPACE_ID_KEY, id);
    } catch (err) {
      setCustomError(getErrorMessage(err, 'Failed to load workspace details.'));
      setActiveWorkspace(null);
      setActiveWorkspaceId(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
    }
  }, [queryClient]);

  const createWorkspace = useCallback(
    async (data: WorkspaceCreateRequest): Promise<WorkspaceDetail> => {
      setCustomError(null);
      try {
        const newWs = await createWsMutation(data);
        await selectWorkspace(newWs.id);
        return newWs;
      } catch (err) {
        const msg = getErrorMessage(err, 'Failed to create workspace.');
        setCustomError(msg);
        throw err;
      }
    },
    [createWsMutation, selectWorkspace]
  );

  const updateWorkspace = useCallback(
    async (id: string, data: WorkspaceUpdateRequest): Promise<WorkspaceDetail> => {
      setCustomError(null);
      try {
        const updated = await updateWsMutation({ id, data });
        if (activeWorkspace?.id === id) {
          setActiveWorkspace(updated);
        }
        return updated;
      } catch (err) {
        const msg = getErrorMessage(err, 'Failed to update workspace.');
        setCustomError(msg);
        throw err;
      }
    },
    [updateWsMutation, activeWorkspace]
  );

  const deleteWorkspace = useCallback(
    async (id: string) => {
      setCustomError(null);
      try {
        await deleteWsMutation(id);
        if (activeWorkspace?.id === id) {
          setActiveWorkspace(null);
          setActiveWorkspaceId(null);
          localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
        }
      } catch (err) {
        const msg = getErrorMessage(err, 'Failed to delete workspace.');
        setCustomError(msg);
        throw err;
      }
    },
    [deleteWsMutation, activeWorkspace]
  );

  // Auto select active workspace when workspaces list loads or changes
  useEffect(() => {
    if (!isAuthenticated) {
      setActiveWorkspace(null);
      setActiveWorkspaceId(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      return;
    }

    if (workspaces.length > 0 && !activeWorkspace) {
      const targetId =
        activeWorkspaceId && workspaces.some((w) => w.id === activeWorkspaceId)
          ? activeWorkspaceId
          : workspaces[0].id;

      selectWorkspace(targetId);
    }
  }, [isAuthenticated, workspaces, activeWorkspace, activeWorkspaceId, selectWorkspace]);

  useEffect(() => {
    const handleGlobalLogout = () => {
      setActiveWorkspace(null);
      setActiveWorkspaceId(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
    };

    window.addEventListener('auth:logout', handleGlobalLogout);
    return () => {
      window.removeEventListener('auth:logout', handleGlobalLogout);
    };
  }, []);

  const combinedError = customError || (listError ? getErrorMessage(listError, 'Failed to list workspaces.') : null);

  const contextValue = useMemo(
    () => ({
      workspaces,
      activeWorkspace,
      isLoading: isListLoading,
      error: combinedError,
      fetchWorkspaces,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      deleteWorkspace,
      clearError,
    }),
    [
      workspaces,
      activeWorkspace,
      isListLoading,
      combinedError,
      fetchWorkspaces,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      deleteWorkspace,
      clearError,
    ]
  );

  return (
    <WorkspaceContext.Provider value={contextValue}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export default WorkspaceContext;
