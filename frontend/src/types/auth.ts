export interface User {
  id: string;
  email: string;
  full_name: string;
  status: string;
  verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password?: string; // Opt for flexibility
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  authenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}
