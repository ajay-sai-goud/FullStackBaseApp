import React, { createContext, useContext } from 'react';
import { AuthContextType, AuthProviderProps } from '../types';
import { useToken } from '../hooks/useToken';
import { usePermissions } from '../hooks/usePermissions';

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Use token management hook
  const { token, setToken, removeToken, isAuthenticated, isLoading } = useToken();

  // Use permissions hook
  const { permissions, hasPermission, hasAnyPermission, hasAllPermissions } = usePermissions(token);

  // Wrapper functions for backward compatibility
  const login = (newToken: string): void => {
    setToken(newToken);
  };

  const logout = (): void => {
    removeToken();
  };

  const value: AuthContextType = {
    token,
    permissions,
    login,
    logout,
    isAuthenticated,
    isLoading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

