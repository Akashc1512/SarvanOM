/**
 * Authentication Hook for React Components
 * 
 * Provides a clean interface for authentication functionality in React components.
 * Follows MAANG standards for state management and error handling.
 */

import { useState, useEffect, useCallback } from "react";
import { authService, type AuthState, type User, type LoginCredentials, type RegisterData } from "@/services/auth";

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>(authService.getAuthState());

  useEffect(() => {
    // Subscribe to auth state changes
    const unsubscribe = authService.subscribe(setAuthState);
    return unsubscribe;
  }, []);

  const login = useCallback(async (credentials: LoginCredentials): Promise<User> => {
    return authService.login(credentials);
  }, []);

  const register = useCallback(async (data: RegisterData): Promise<User> => {
    return authService.register(data);
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    return authService.logout();
  }, []);

  const hasPermission = useCallback((permission: string): boolean => {
    return authService.hasPermission(permission);
  }, []);

  const hasRole = useCallback((role: string): boolean => {
    return authService.hasRole(role);
  }, []);

  const getAuthHeader = useCallback(() => {
    return authService.getAuthHeader();
  }, []);

  return {
    // State
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    error: authState.error,
    
    // Actions
    login,
    register,
    logout,
    
    // Utilities
    hasPermission,
    hasRole,
    getAuthHeader,
  };
} 