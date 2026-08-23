import { env } from './env';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  roles: string[];
  permissions: string[];
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export class ApiError extends Error {
  statusCode: number;
  constructor(message: string, statusCode: number = 400) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${env.NEXT_PUBLIC_API_URL}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = 'An error occurred during the request.';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      errorMessage = `Server returned HTTP ${response.status}: ${response.statusText}`;
    }
    throw new ApiError(errorMessage, response.status);
  }

  return response.json();
}

// Authentication API Endpoints
export const authApi = {
  register: (payload: RegisterPayload) =>
    request<TokenResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  login: (payload: LoginPayload) =>
    request<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  refresh: (refreshToken: string) =>
    request<TokenResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logout: (refreshToken: string) =>
    request<{ message: string; status: string }>('/api/v1/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logoutAll: (accessToken: string) =>
    request<{ message: string; status: string }>('/api/v1/auth/logout-all', {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
    }),

  getMe: (accessToken: string) =>
    request<UserProfile>('/api/v1/auth/me', {
      method: 'GET',
      headers: { Authorization: `Bearer ${accessToken}` },
    }),

  changePassword: (accessToken: string, payload: ChangePasswordPayload) =>
    request<{ message: string; status: string }>('/api/v1/auth/change-password', {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(payload),
    }),
};

// User Profile API Endpoints
export const usersApi = {
  getMe: (accessToken: string) =>
    request<UserProfile>('/api/v1/users/me', {
      method: 'GET',
      headers: { Authorization: `Bearer ${accessToken}` },
    }),

  updateMe: (accessToken: string, payload: { first_name?: string; last_name?: string }) =>
    request<UserProfile>('/api/v1/users/me', {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(payload),
    }),
};

export async function fetchHealth() {
  return request<{ status: string; service: string; version: string }>('/health');
}
