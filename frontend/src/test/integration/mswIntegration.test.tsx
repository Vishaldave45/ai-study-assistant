import { describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';
import { server } from '../mocks/server';

describe('MSW Integration Layer', () => {
  beforeEach(() => {
    server.listen();
  });

  it('intercepts auth login network calls via MSW server', async () => {
    const res = await axios.post('/api/v1/auth/token', {
      username: 'student@example.com',
      password: 'Password123!',
    });

    expect(res.data.access_token).toBe('mock-access-token-123');
    expect(res.data.user.email).toBe('student@example.com');
  });

  it('intercepts workspace list network calls via MSW server', async () => {
    const res = await axios.get('/api/v1/workspaces');

    expect(res.data.items).toHaveLength(1);
    expect(res.data.items[0].name).toBe('Physics 101');
  });
});
