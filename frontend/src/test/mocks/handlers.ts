export const handlers = [
  {
    path: '/api/v1/auth/token',
    method: 'POST',
    response: {
      access_token: 'mock-access-token-123',
      refresh_token: 'mock-refresh-token-456',
      token_type: 'bearer',
      user: {
        id: 'u-123',
        email: 'student@example.com',
        full_name: 'Student Developer',
      },
    },
  },
  {
    path: '/api/v1/workspaces',
    method: 'GET',
    response: {
      items: [{ id: 'ws-1', name: 'Physics 101', description: 'Mechanics' }],
      total: 1,
      page: 1,
      page_size: 100,
    },
  },
];
