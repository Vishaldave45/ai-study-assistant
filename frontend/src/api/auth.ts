import apiClient from './client';
import type {
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
  LogoutRequest,
  LogoutResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  MessageResponse,
  User,
} from '../types/auth';

/**
 * Authentication API methods wrapper.
 */
export const authApi = {
  /**
   * Registers a new user account.
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Logs a user in with email and password.
   */
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  /**
   * Invalidates the active refresh token and logs the user out.
   */
  logout: async (data: LogoutRequest): Promise<LogoutResponse> => {
    const response = await apiClient.post<LogoutResponse>('/auth/logout', data);
    return response.data;
  },

  /**
   * Fetches the profile details of the current logged-in user.
   */
  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Submits a password reset request for a given email address.
   */
  forgotPassword: async (data: ForgotPasswordRequest): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>('/auth/forgot-password', data);
    return response.data;
  },

  /**
   * Resets the user's password using the generated token.
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>('/auth/reset-password', data);
    return response.data;
  },
};
