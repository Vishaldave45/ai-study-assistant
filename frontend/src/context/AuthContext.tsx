import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginRequest, RegisterRequest, AuthContextType } from '../types/auth';
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  refresh as apiRefresh,
} from '../api/auth';
import {
  saveAccessToken,
  saveRefreshToken,
  getRefreshToken,
  clearTokens,
} from '../utils/storage';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const authenticated = !!user;

  // Initialize session on load
  useEffect(() => {
    const initializeAuth = async () => {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        setLoading(false);
        return;
      }

      try {
        // Attempt token refresh on startup
        const tokenData = await apiRefresh(refreshToken);
        saveAccessToken(tokenData.access_token);
        saveRefreshToken(tokenData.refresh_token);

        // Fetch current user details
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        console.error('Session initialization failed:', err);
        clearTokens();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    setLoading(true);
    try {
      const response = await apiLogin(credentials);
      saveAccessToken(response.access_token);
      saveRefreshToken(response.refresh_token);

      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      setUser(null);
      clearTokens();
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    setLoading(true);
    try {
      await apiRegister(data);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await apiLogout(refreshToken);
      } catch (err) {
        console.error('Logout API call failed:', err);
      }
    }
    clearTokens();
    setUser(null);
    setLoading(false);
  };

  const refreshUser = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      console.error('Failed to refresh user info:', err);
      throw err;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authenticated,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
