import { Navigate } from 'react-router-dom';
import type { ReactNode } from 'react'
import { useAuth } from '../contexts/AuthContext';

export function ProtectedRoute({ children, role }: { children: ReactNode; role?: 'user' | 'admin' }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return <>{children}</>;
}