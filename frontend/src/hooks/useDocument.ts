import { useContext } from 'react';
import { DocumentContext } from '../contexts/DocumentContext.tsx';


export function useDocument() {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
}
export default useDocument;
