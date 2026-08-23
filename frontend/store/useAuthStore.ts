import { create } from 'zustand';
import { authApi, usersApi, UserProfile, RegisterPayload, LoginPayload, ApiError } from '@/lib/api';

interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  fetchUser: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
  initializeAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  initializeAuth: async () => {
    if (typeof window === 'undefined') return;

    const storedAccess = localStorage.getItem('aitradeq_access_token');
    const storedRefresh = localStorage.getItem('aitradeq_refresh_token');

    if (!storedAccess || !storedRefresh) {
      set({ isAuthenticated: false, user: null, isLoading: false });
      return;
    }

    set({ accessToken: storedAccess, refreshToken: storedRefresh, isLoading: true });

    try {
      const userProfile = await authApi.getMe(storedAccess);
      set({ user: userProfile, isAuthenticated: true, isLoading: false, error: null });
    } catch {
      // Try refresh
      const refreshed = await get().refreshSession();
      if (!refreshed) {
        get().logout();
      }
      set({ isLoading: false });
    }
  },

  login: async (payload: LoginPayload) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await authApi.login(payload);
      if (typeof window !== 'undefined') {
        localStorage.setItem('aitradeq_access_token', tokenData.access_token);
        localStorage.setItem('aitradeq_refresh_token', tokenData.refresh_token);
      }

      set({
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        isAuthenticated: true,
      });

      const userProfile = await authApi.getMe(tokenData.access_token);
      set({ user: userProfile, isLoading: false, error: null });
    } catch (err: unknown) {
      const message = err instanceof ApiError ? err.message : 'Login failed. Please check your credentials.';
      set({ error: message, isLoading: false, isAuthenticated: false, user: null });
      throw err;
    }
  },

  register: async (payload: RegisterPayload) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await authApi.register(payload);
      if (typeof window !== 'undefined') {
        localStorage.setItem('aitradeq_access_token', tokenData.access_token);
        localStorage.setItem('aitradeq_refresh_token', tokenData.refresh_token);
      }

      set({
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        isAuthenticated: true,
      });

      const userProfile = await authApi.getMe(tokenData.access_token);
      set({ user: userProfile, isLoading: false, error: null });
    } catch (err: unknown) {
      const message = err instanceof ApiError ? err.message : 'Registration failed. Please check your details.';
      set({ error: message, isLoading: false, isAuthenticated: false, user: null });
      throw err;
    }
  },

  refreshSession: async (): Promise<boolean> => {
    const currentRefresh = get().refreshToken || (typeof window !== 'undefined' ? localStorage.getItem('aitradeq_refresh_token') : null);
    if (!currentRefresh) {
      return false;
    }

    try {
      const tokenData = await authApi.refresh(currentRefresh);
      if (typeof window !== 'undefined') {
        localStorage.setItem('aitradeq_access_token', tokenData.access_token);
        localStorage.setItem('aitradeq_refresh_token', tokenData.refresh_token);
      }

      set({
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        isAuthenticated: true,
      });

      const userProfile = await authApi.getMe(tokenData.access_token);
      set({ user: userProfile, error: null });
      return true;
    } catch {
      return false;
    }
  },

  fetchUser: async () => {
    const token = get().accessToken;
    if (!token) return;

    try {
      const userProfile = await authApi.getMe(token);
      set({ user: userProfile, isAuthenticated: true });
    } catch {
      const refreshed = await get().refreshSession();
      if (!refreshed) {
        get().logout();
      }
    }
  },

  logout: async () => {
    const rf = get().refreshToken;
    if (rf) {
      try {
        await authApi.logout(rf);
      } catch {
        // Silently ignore logout errors on client teardown
      }
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem('aitradeq_access_token');
      localStorage.removeItem('aitradeq_refresh_token');
    }

    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
      isLoading: false,
    });
  },

  logoutAll: async () => {
    const at = get().accessToken;
    if (at) {
      try {
        await authApi.logoutAll(at);
      } catch {
        // Silently ignore
      }
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem('aitradeq_access_token');
      localStorage.removeItem('aitradeq_refresh_token');
    }

    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
      isLoading: false,
    });
  },
}));
