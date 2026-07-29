import { describe, it, expect, beforeEach } from 'vitest';
import authReducer, { setCredentials, setUser, logout, setLoading } from './authSlice';

describe('authSlice Reducer', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('handles initial state correctly', () => {
    const state = authReducer(undefined, { type: 'unknown' });
    expect(state).toEqual({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('updates credentials and saves tokens on setCredentials', () => {
    const mockUser = { id: 'u1', email: 'test@example.com', full_name: 'Test User' };
    const state = authReducer(
      undefined,
      setCredentials({ user: mockUser, access_token: 'access-123', refresh_token: 'refresh-456' })
    );

    expect(state.user).toEqual(mockUser);
    expect(state.token).toBe('access-123');
    expect(state.isAuthenticated).toBe(true);

    expect(localStorage.getItem('ai_study_access_token')).toBe('access-123');
    expect(localStorage.getItem('ai_study_refresh_token')).toBe('refresh-456');
  });

  it('sets user details with setUser action', () => {
    const mockUser = { id: 'u2', email: 'user2@example.com' };
    const state = authReducer(undefined, setUser(mockUser));

    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('clears state and localStorage tokens on logout', () => {
    localStorage.setItem('ai_study_access_token', 'token-123');
    const initialState = { user: { id: 'u1', email: 'test@example.com' }, token: 'token-123', isAuthenticated: true, isLoading: false };

    const state = authReducer(initialState, logout());
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);

    expect(localStorage.getItem('ai_study_access_token')).toBeNull();
  });

  it('toggles isLoading flag with setLoading action', () => {
    const state = authReducer(undefined, setLoading(true));
    expect(state.isLoading).toBe(true);
  });
});
