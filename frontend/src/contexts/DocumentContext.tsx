import { createContext, useState, useEffect, useMemo, useCallback } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { documentApi } from '../api/document.ts';
import { useWorkspace } from '../hooks/useWorkspace.ts';
import type { DocumentItem } from '../types/document.ts';

interface DocumentContextType {
  documents: DocumentItem[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  totalPages: number;
  fetchDocuments: (page?: number, query?: string) => Promise<void>;
  uploadDocument: (file: File) => Promise<DocumentItem>;
  deleteDocument: (id: string) => Promise<void>;
  clearError: () => void;
}

export const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export function DocumentProvider({ children }: { children: ReactNode }) {
  const { activeWorkspace } = useWorkspace();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination states
  const [totalCount, setTotalCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  const clearError = useCallback(() => setError(null), []);

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


  const fetchDocuments = useCallback(
    async (page: number = 1, query?: string) => {
      if (!activeWorkspace) {
        setDocuments([]);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const res = await documentApi.list(activeWorkspace.id, {
          page,
          page_size: 10,
          query,
        });
        setDocuments(res.items);
        setTotalCount(res.total);
        setCurrentPage(res.page);
        setTotalPages(res.total_pages);
      } catch (err) {
        setError(getErrorMessage(err, 'Failed to fetch documents.'));
      } finally {
        setIsLoading(false);
      }
    },
    [activeWorkspace]
  );

  /**
   * Upload -active workspace
   */
  const uploadDocument = useCallback(
    async (file: File): Promise<DocumentItem> => {
      if (!activeWorkspace) {
        const errMsg = 'Cannot upload document: No active workspace selected.';
        setError(errMsg);
        throw new Error(errMsg);
      }

      setIsLoading(true);
      setError(null);
      try {
        const newDoc = await documentApi.upload(activeWorkspace.id, file);
        // Refresh list
        await fetchDocuments(1);
        return newDoc;
      } catch (err) {
        const errMsg = getErrorMessage(err, 'Failed to upload document.');
        setError(errMsg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [activeWorkspace, fetchDocuments]
  );

  /**
   * Delete 
   */
  const deleteDocument = useCallback(
    async (id: string) => {
      setIsLoading(true);
      setError(null);
      try {
        await documentApi.delete(id);
        // Refresh list on current page 
        const targetPage = documents.length === 1 && currentPage > 1 ? currentPage - 1 : currentPage;
        await fetchDocuments(targetPage);
      } catch (err) {
        const errMsg = getErrorMessage(err, 'Failed to delete document.');
        setError(errMsg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [documents.length, currentPage, fetchDocuments]
  );

  // Sync documents list when the selected workspace changes
  useEffect(() => {
    if (!activeWorkspace) {
      setDocuments([]);
      setTotalCount(0);
      setCurrentPage(1);
      setTotalPages(1);
      setError(null);
      return;
    }

    fetchDocuments(1);
  }, [activeWorkspace, fetchDocuments]);

  const contextValue = useMemo(
    () => ({
      documents,
      isLoading,
      error,
      totalCount,
      currentPage,
      totalPages,
      fetchDocuments,
      uploadDocument,
      deleteDocument,
      clearError,
    }),
    [
      documents,
      isLoading,
      error,
      totalCount,
      currentPage,
      totalPages,
      fetchDocuments,
      uploadDocument,
      deleteDocument,
      clearError,
    ]
  );

  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
}
export default DocumentContext;
