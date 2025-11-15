import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for managing JWT token storage and expiration.
 * Handles token persistence in localStorage and expiration checking.
 */
export const useToken = () => {
  const [token, setTokenState] = useState<string | null>(() => {
    // Initialize token from localStorage
    return localStorage.getItem('token') || null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check token expiration on mount
  useEffect(() => {
    const checkTokenExpiration = (): void => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          // Decode JWT token to check expiration
          const payload = JSON.parse(atob(storedToken.split('.')[1]));
          const exp = payload.exp * 1000; // Convert to milliseconds
          const now = Date.now();

          if (exp < now) {
            // Token expired
            setTokenState(null);
            localStorage.removeItem('token');
          } else {
            setTokenState(storedToken);
          }
        } catch (error) {
          // Invalid token format
          setTokenState(null);
          localStorage.removeItem('token');
        }
      }
      setIsLoading(false);
    };

    checkTokenExpiration();
  }, []);

  const setToken = useCallback((newToken: string): void => {
    setTokenState(newToken);
    localStorage.setItem('token', newToken);
  }, []);

  const removeToken = useCallback((): void => {
    setTokenState(null);
    localStorage.removeItem('token');
  }, []);

  const isAuthenticated = useCallback((): boolean => {
    return token !== null;
  }, [token]);

  return {
    token,
    setToken,
    removeToken,
    isAuthenticated,
    isLoading,
  };
};

