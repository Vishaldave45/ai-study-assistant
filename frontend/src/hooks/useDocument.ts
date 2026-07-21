import { useContext } from 'react';
import { DocumentContext } from '../contexts/DocumentContext.tsx';

/**
 * Custom hook to safely consume the DocumentContext.
 * Throws an error if used outside a DocumentProvider.
 */
export function useDocument() {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
}
export default useDocument;
