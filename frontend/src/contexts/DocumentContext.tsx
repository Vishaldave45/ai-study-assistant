import { createContext, useState, useMemo, useCallback } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { useWorkspace } from '../hooks/useWorkspace.ts';
import { useServerDocumentsQuery } from '../hooks/useServerDocumentsQuery';
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
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string | undefined>(undefined);
  const [customError, setCustomError] = useState<string | null>(null);

  const {
    data: docData,
    isLoading,
    error: queryError,
    uploadDocument: uploadMutation,
    deleteDocument: deleteMutation,
  } = useServerDocumentsQuery({
    workspaceId: activeWorkspace?.id || null,
    page: currentPage,
    pageSize: 10,
    query: searchQuery,
  });

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

  const fetchDocuments = useCallback(async (page: number = 1, query?: string) => {
    setCurrentPage(page);
    setSearchQuery(query);
  }, []);

  const uploadDocument = useCallback(
    async (file: File): Promise<DocumentItem> => {
      setCustomError(null);
      try {
        const newDoc = await uploadMutation(file);
        setCurrentPage(1);
        return newDoc;
      } catch (err) {
        const msg = getErrorMessage(err, 'Failed to upload document.');
        setCustomError(msg);
        throw err;
      }
    },
    [uploadMutation]
  );

  const deleteDocument = useCallback(
    async (id: string) => {
      setCustomError(null);
      try {
        await deleteMutation(id);
      } catch (err) {
        const msg = getErrorMessage(err, 'Failed to delete document.');
        setCustomError(msg);
        throw err;
      }
    },
    [deleteMutation]
  );

  const combinedError = customError || (queryError ? getErrorMessage(queryError, 'Failed to fetch documents.') : null);

  const contextValue = useMemo(
    () => ({
      documents: docData?.items || [],
      isLoading,
      error: combinedError,
      totalCount: docData?.total || 0,
      currentPage: docData?.page || currentPage,
      totalPages: docData?.total_pages || 1,
      fetchDocuments,
      uploadDocument,
      deleteDocument,
      clearError,
    }),
    [
      docData,
      isLoading,
      combinedError,
      currentPage,
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
