import { vi } from 'vitest';
import axios from 'axios';

export const server = {
  listen: (_options?: { onUnhandledRequest?: string }) => {
    vi.spyOn(axios, 'post').mockImplementation(async (url: string) => {
      if (url === '/api/v1/auth/token') {
        return {
          data: {
            access_token: 'mock-access-token-123',
            refresh_token: 'mock-refresh-token-456',
            token_type: 'bearer',
            user: {
              id: 'u-123',
              email: 'student@example.com',
              full_name: 'Student Developer',
            },
          },
          status: 200,
          statusText: 'OK',
          headers: {},
          config: {} as any,
        };
      }
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config: {} as any };
    });

    vi.spyOn(axios, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/workspaces') {
        return {
          data: {
            items: [{ id: 'ws-1', name: 'Physics 101', description: 'Mechanics' }],
            total: 1,
            page: 1,
            page_size: 100,
          },
          status: 200,
          statusText: 'OK',
          headers: {},
          config: {} as any,
        };
      }
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config: {} as any };
    });
  },
  resetHandlers: () => {
    vi.restoreAllMocks();
  },
  close: () => {
    vi.restoreAllMocks();
  },
};
