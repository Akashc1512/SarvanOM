"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { LoadingSpinner } from "@/components/atoms/loading-spinner";

interface RouteGuardProps {
  children: React.ReactNode;
  requiredRole?: "user" | "admin" | "expert";
  fallback?: React.ReactNode;
}

interface User {
  id: string;
  email: string;
  role: "user" | "admin" | "expert";
  permissions: string[];
}

// Mock authentication hook - replace with real auth
function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate auth check
    const checkAuth = async () => {
      try {
        // Check for auth token
        const token = localStorage.getItem("auth_token");
        if (token) {
          // Mock user data - replace with real API call
          setUser({
            id: "1",
            email: "user@example.com",
            role: "user",
            permissions: ["read", "write"],
          });
        }
      } catch (error) {
        console.error("Auth check failed:", error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return { user, loading };
}

export function RouteGuard({
  children,
  requiredRole,
  fallback,
}: RouteGuardProps) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading) {
      // Check if user is authenticated
      if (!user) {
        // Redirect to login if not authenticated
        router.push("/login?redirect=" + encodeURIComponent(pathname));
        return;
      }

      // Check role-based access
      if (requiredRole && user.role !== requiredRole && user.role !== "admin") {
        // Redirect to unauthorized page
        router.push("/unauthorized");
        return;
      }
    }
  }, [user, loading, requiredRole, router, pathname]);

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show fallback if user is not authenticated
  if (!user) {
    return (
      fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Redirecting to login...</p>
          </div>
        </div>
      )
    );
  }

  // Check role-based access
  if (requiredRole && user.role !== requiredRole && user.role !== "admin") {
    return (
      fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">
              Access Denied
            </h1>
            <p className="text-gray-600">
              You don&apos;t have permission to access this page.
            </p>
          </div>
        </div>
      )
    );
  }

  return <>{children}</>;
}
