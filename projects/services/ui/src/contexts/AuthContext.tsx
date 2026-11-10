import { useState } from 'react';
import type { ReactNode } from 'react'
import { api } from '../api/client';
import type { AuthUser } from '../types';
import { AuthContext } from '../hooks/useAuthContext';


const STORAGE_KEY = 'boardgames.auth';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  });

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password);
    const authUser: AuthUser = {
      user_id: data.user_id,
      email: data.email,
      role: data.role as 'user' | 'admin',
      token: data.access_token,
    };
    setUser(authUser);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(authUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}