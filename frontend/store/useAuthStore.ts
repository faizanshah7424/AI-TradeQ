import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  user: { email: string; role: string } | null;
  setAuth: (user: { email: string; role: string } | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  setAuth: (user) => set({ isAuthenticated: !!user, user }),
  logout: () => set({ isAuthenticated: false, user: null }),
}));
