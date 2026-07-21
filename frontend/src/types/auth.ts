/**
 * User account status enum.
 */
export const UserStatus = {
  ACTIVE: 'active',
  PENDING_VERIFICATION: 'pending_verification',
  SUSPENDED: 'suspended',
} as const;

export type UserStatus = typeof UserStatus[keyof typeof UserStatus];

/**
 * Interface representing a user profile.
 */
export interface User {
  id: string;
  email: string;
  full_name: string;
  status: UserStatus;
  is_verified: boolean;
  created_at: string;
}

/**
 * Request payload for user registration.
 */
export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

/**
 * Response payload returned after registration.
 */
export interface RegisterResponse {
  message: string;
}

/**
 * Request payload for logging in.
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Token payload containing JWT session tokens.
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * Request payload for refreshing the JWT access token.
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Request payload for logging out.
 */
export interface LogoutRequest {
  refresh_token: string;
}

/**
 * Response returned after logging out.
 */
export interface LogoutResponse {
  message: string;
}

/**
 * Request payload for forgot password.
 */
export interface ForgotPasswordRequest {
  email: string;
}

/**
 * Request payload for reset password.
 */
export interface ResetPasswordRequest {
  token: string;
  password: string;
}

/**
 * General message response returned by generic endpoints.
 */
export interface MessageResponse {
  message: string;
}
