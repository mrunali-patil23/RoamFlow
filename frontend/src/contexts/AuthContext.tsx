import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import ApiService, { AuthenticationError, NetworkError } from '../services/apiService';

interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    
    setLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.login(username, password);
      
      // Update state
      setToken(response.access_token);
      setUser(response.user);
      
      return true;
    } catch (err: any) {
      let errorMessage = 'Login failed';
      
      if (err instanceof AuthenticationError) {
        errorMessage = 'Invalid username or password';
      } else if (err instanceof NetworkError) {
        errorMessage = 'Unable to connect to server. Please check your internet connection.';
      } else {
        errorMessage = err.message || 'Login failed';
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.register(username, email, password);
      
      // Update state
      setToken(response.access_token);
      setUser(response.user);
      
      return true;
    } catch (err: any) {
      let errorMessage = 'Registration failed';
      
      if (err instanceof AuthenticationError) {
        errorMessage = 'Username or email already exists';
      } else if (err instanceof NetworkError) {
        errorMessage = 'Unable to connect to server. Please check your internet connection.';
      } else {
        errorMessage = err.message || 'Registration failed';
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Call API logout (async but don't wait)
    ApiService.logout().catch(console.error);
    
    // Clear state
    setToken(null);
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};