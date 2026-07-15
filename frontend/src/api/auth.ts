import axiosInstance from './axios';
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '../types/auth';

export const login = async (data: LoginRequest): Promise<TokenResponse> => {
  const response = await axiosInstance.post<TokenResponse>('/auth/login', data);
  return response.data;
};

export const register = async (data: RegisterRequest): Promise<{ message: string }> => {
  const response = await axiosInstance.post<{ message: string }>('/auth/register', data);
  return response.data;
};

export const refresh = async (refreshToken: string): Promise<TokenResponse> => {
  const response = await axiosInstance.post<TokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  return response.data;
};

export const logout = async (refreshToken: string): Promise<{ message: string }> => {
  const response = await axiosInstance.post<{ message: string }>('/auth/logout', {
    refresh_token: refreshToken,
  });
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await axiosInstance.get<User>('/auth/me');
  return response.data;
};
