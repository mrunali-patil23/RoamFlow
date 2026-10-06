import React, { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children, fallback }) => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If user is not authenticated, redirect to auth page
  if (!user) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    // Redirect to /auth page instead of showing inline login
    navigate('/auth');
    return null;
  }

  // User is authenticated, render children
  return <>{children}</>;
};

export default AuthGuard;