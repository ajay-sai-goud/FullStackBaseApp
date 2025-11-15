import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ProtectedRouteProps } from '../types';
import { Permissions } from '../utils/permissions';

/**
 * ProtectedRoute component that checks authentication and permissions
 * Redirects to /login if not authenticated
 * Redirects to first accessible page if permission denied
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredPermission }) => {
  const { isAuthenticated, isLoading, hasAnyPermission } = useAuth();

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  // Check permission if required (admin grants all permissions)
  if (requiredPermission && !hasAnyPermission(requiredPermission, Permissions.ADMIN)) {
    // Redirect to first accessible page based on permissions
    if (hasAnyPermission(Permissions.READ_AUDIO, Permissions.ADMIN)) {
      return <Navigate to="/audio" replace />;
    } else if (hasAnyPermission(Permissions.READ_USER, Permissions.ADMIN)) {
      return <Navigate to="/users" replace />;
    } else {
      // No accessible pages, redirect to login
      return <Navigate to="/login" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;

