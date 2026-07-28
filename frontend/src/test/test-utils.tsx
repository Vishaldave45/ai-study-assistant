import React, { type PropsWithChildren } from 'react';
import { render, type RenderOptions } from '@testing-library/react';

import { Provider } from 'react-redux';
import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import authReducer from '../redux/slices/authSlice';
import workspaceReducer from '../redux/slices/workspaceSlice';
import uiReducer from '../redux/slices/uiSlice';
import type { RootState } from '../redux/store';

import { AuthProvider } from '../contexts/AuthContext';
import { WorkspaceProvider } from '../contexts/WorkspaceContext';
import { DocumentProvider } from '../contexts/DocumentContext';
import { ChatProvider } from '../contexts/ChatContext';

const rootReducer = combineReducers({
  auth: authReducer,
  workspace: workspaceReducer,
  ui: uiReducer,
});

interface ExtendedRenderOptions extends Omit<RenderOptions, 'queries'> {
  preloadedState?: Partial<RootState>;
  store?: ReturnType<typeof createTestStore>;
  initialEntries?: string[];
}

export function createTestStore(preloadedState?: Partial<RootState>) {
  return configureStore({
    reducer: rootReducer,
    preloadedState,
  });
}


export function renderWithProviders(
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = createTestStore(preloadedState),
    initialEntries = ['/'],
    ...renderOptions
  }: ExtendedRenderOptions = {}
) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  function Wrapper({ children }: PropsWithChildren<{}>): React.ReactElement {
    return (
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <WorkspaceProvider>
              <DocumentProvider>
                <ChatProvider>
                  <MemoryRouter initialEntries={initialEntries}>
                    {children}
                  </MemoryRouter>
                </ChatProvider>
              </DocumentProvider>
            </WorkspaceProvider>
          </AuthProvider>
        </QueryClientProvider>
      </Provider>
    );
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}




export { renderWithProviders as render };
export * from '@testing-library/react';
export { userEvent } from '@testing-library/user-event';


