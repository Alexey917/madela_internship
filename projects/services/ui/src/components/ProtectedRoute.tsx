import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuthContext';
import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  role?: 'user' | 'admin';
}

export function ProtectedRoute({ children, role }: Props) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}