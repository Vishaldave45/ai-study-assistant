import { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { authApi } from '../api/auth';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../config';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../types/auth';

/**
 * Context value interface for Authentication.
 */
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (details: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: ForgotPasswordRequest) => Promise<void>;
  resetPassword: (payload: ResetPasswordRequest) => Promise<void>;
  clearError: () => void;
}

// Create the context with undefined as default to enforce provider usage
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Helper to extract descriptive error messages from backend API errors safely.
 */
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

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  // Silent session re-hydration on application mount
  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.getMe();
        setUser(currentUser);
      } catch (err: unknown) {
        // Token was invalid or expired, clean up session
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Listen to global logout event dispatched by Axios interceptor
  useEffect(() => {
    const handleGlobalLogout = () => {
      setUser(null);
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    };

    window.addEventListener('auth:logout', handleGlobalLogout);
    return () => {
      window.removeEventListener('auth:logout', handleGlobalLogout);
    };
  }, []);

  /**
   * Submits user credentials and starts session.
   */
  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokens = await authApi.login(credentials);
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);

      const currentUser = await authApi.getMe();
      setUser(currentUser);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err, 'Failed to login. Please check your credentials.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Submits registration details to backend.
   */
  const register = async (details: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.register(details);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err, 'Failed to register account.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Log out active session and clear token storage.
   */
  const logout = async () => {
    setIsLoading(true);
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    try {
      if (refreshToken) {
        await authApi.logout({ refresh_token: refreshToken });
      }
    } catch (err) {
      // Log out locally even if API invalidation fails
      console.error('API logout failed, clearing local session:', err);
    } finally {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      setUser(null);
      setIsLoading(false);
      setError(null);
    }
  };

  /**
   * Initiates forgot password flow.
   */
  const forgotPassword = async (payload: ForgotPasswordRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.forgotPassword(payload);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err, 'Failed to submit password reset request.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Completes password reset flow using token.
   */
  const resetPassword = async (payload: ResetPasswordRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(payload);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err, 'Failed to reset password.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        forgotPassword,
        resetPassword,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
