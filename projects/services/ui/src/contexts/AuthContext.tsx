import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { AuthUser } from '../types';
import { api } from '../api/client'

interface AuthContextValue {
  user: AuthUser | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const stored = localStorage.getItem('auth');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password);
    const authUser: AuthUser = {
      user_id: data.user_id,
      role: data.role as 'user' | 'admin',
      token: data.access_token,
    };
    setUser(authUser);
    localStorage.setItem('auth', JSON.stringify(authUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth');
  };

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}