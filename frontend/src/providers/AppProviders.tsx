import type { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { store } from '../redux/store';
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
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <WorkspaceProvider>
            <DocumentProvider>
              <ChatProvider>{children}</ChatProvider>
            </DocumentProvider>
          </WorkspaceProvider>
        </AuthProvider>
      </QueryClientProvider>
    </Provider>
  );
}

export default AppProviders;
