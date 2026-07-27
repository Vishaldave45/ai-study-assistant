import type { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../contexts/AuthContext';
import { WorkspaceProvider } from '../contexts/WorkspaceContext';
import { DocumentProvider } from '../contexts/DocumentContext';
import { ChatProvider } from '../contexts/ChatContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WorkspaceProvider>
          <DocumentProvider>
            <ChatProvider>{children}</ChatProvider>
          </DocumentProvider>
        </WorkspaceProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default AppProviders;
