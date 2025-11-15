import { useMemo, useCallback } from 'react';

/**
 * Hook for extracting and checking user permissions from JWT token.
 * Handles permission extraction and provides permission checking functions.
 */
export const usePermissions = (token: string | null) => {
  // Extract permissions from token
  const permissions = useMemo(() => {
    if (!token) {
      return [];
    }
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const perms = payload.permissions;
      if (Array.isArray(perms)) {
        return perms;
      }
      return [];
    } catch (error) {
      return [];
    }
  }, [token]);

  // Permission checking functions
  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!token || permissions.length === 0) {
        return false;
      }
      // Admin permission grants all permissions
      if (permissions.includes('admin')) {
        return true;
      }
      return permissions.includes(permission);
    },
    [token, permissions]
  );

  const hasAnyPermission = useCallback(
    (...requiredPermissions: string[]): boolean => {
      if (!token || permissions.length === 0) {
        return false;
      }
      // Admin permission grants all permissions
      if (permissions.includes('admin')) {
        return true;
      }
      return requiredPermissions.some((perm) => permissions.includes(perm));
    },
    [token, permissions]
  );

  const hasAllPermissions = useCallback(
    (...requiredPermissions: string[]): boolean => {
      if (!token || permissions.length === 0) {
        return false;
      }
      // Admin permission grants all permissions
      if (permissions.includes('admin')) {
        return true;
      }
      return requiredPermissions.every((perm) => permissions.includes(perm));
    },
    [token, permissions]
  );

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
};

