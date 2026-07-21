import { createContext, useState, useEffect, useMemo } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { workspaceApi } from '../api/workspace';
import { useAuth } from '../hooks/useAuth';
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
  const [workspaces, setWorkspaces] = useState<WorkspaceSummary[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  // Helper to extract Axios error messages safely
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

  /**
   * Load workspaces from backend.
   */
  const fetchWorkspaces = async (query?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await workspaceApi.list({ query, page_size: 100 }); // fetch up to 100 workspaces for selection list
      setWorkspaces(res.items);
      
      // If we have an active workspace loaded but it's no longer in the list, clear it
      if (activeWorkspace && !res.items.some((w) => w.id === activeWorkspace.id)) {
        setActiveWorkspace(null);
        localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to retrieve workspaces.'));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Select a workspace and load its full details.
   */
  const selectWorkspace = async (id: string | null) => {
    if (!id) {
      setActiveWorkspace(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const details = await workspaceApi.get(id);
      setActiveWorkspace(details);
      localStorage.setItem(ACTIVE_WORKSPACE_ID_KEY, id);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load workspace details.'));
      setActiveWorkspace(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Create a new workspace.
   */
  const createWorkspace = async (data: WorkspaceCreateRequest): Promise<WorkspaceDetail> => {
    setIsLoading(true);
    setError(null);
    try {
      const newWs = await workspaceApi.create(data);
      // Refresh list
      await fetchWorkspaces();
      // Auto-select the newly created workspace
      await selectWorkspace(newWs.id);
      return newWs;
    } catch (err) {
      const errMsg = getErrorMessage(err, 'Failed to create workspace.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Rename or update workspace.
   */
  const updateWorkspace = async (id: string, data: WorkspaceUpdateRequest): Promise<WorkspaceDetail> => {
    setIsLoading(true);
    setError(null);
    try {
      const updatedWs = await workspaceApi.update(id, data);
      await fetchWorkspaces();
      if (activeWorkspace?.id === id) {
        setActiveWorkspace(updatedWs);
      }
      return updatedWs;
    } catch (err) {
      const errMsg = getErrorMessage(err, 'Failed to update workspace.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Delete a workspace.
   */
  const deleteWorkspace = async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await workspaceApi.delete(id);
      await fetchWorkspaces();
      if (activeWorkspace?.id === id) {
        setActiveWorkspace(null);
        localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      }
    } catch (err) {
      const errMsg = getErrorMessage(err, 'Failed to delete workspace.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Re-hydrate last active workspace and load workspaces on login
  useEffect(() => {
    if (!isAuthenticated) {
      setWorkspaces([]);
      setActiveWorkspace(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
      return;
    }

    const initWorkspaces = async () => {
      setIsLoading(true);
      try {
        const res = await workspaceApi.list({ page_size: 100 });
        setWorkspaces(res.items);

        const lastActiveId = localStorage.getItem(ACTIVE_WORKSPACE_ID_KEY);
        if (lastActiveId && res.items.some((w) => w.id === lastActiveId)) {
          const details = await workspaceApi.get(lastActiveId);
          setActiveWorkspace(details);
        } else if (res.items.length > 0) {
          // Default to first workspace if no cached workspace exists
          const details = await workspaceApi.get(res.items[0].id);
          setActiveWorkspace(details);
          localStorage.setItem(ACTIVE_WORKSPACE_ID_KEY, res.items[0].id);
        }
      } catch (err) {
        console.error('Failed to initialize workspaces:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initWorkspaces();
  }, [isAuthenticated]);

  // Listen to global logout to clear states immediately
  useEffect(() => {
    const handleGlobalLogout = () => {
      setWorkspaces([]);
      setActiveWorkspace(null);
      localStorage.removeItem(ACTIVE_WORKSPACE_ID_KEY);
    };

    window.addEventListener('auth:logout', handleGlobalLogout);
    return () => {
      window.removeEventListener('auth:logout', handleGlobalLogout);
    };
  }, []);

  // Memoize value to optimize rendering and prevent unnecessary triggers in children
  const contextValue = useMemo(
    () => ({
      workspaces,
      activeWorkspace,
      isLoading,
      error,
      fetchWorkspaces,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      deleteWorkspace,
      clearError,
    }),
    [workspaces, activeWorkspace, isLoading, error]
  );

  return (
    <WorkspaceContext.Provider value={contextValue}>
      {children}
    </WorkspaceContext.Provider>
  );
}
