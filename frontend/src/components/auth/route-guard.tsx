"use client";

import React, { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { LoadingSpinner } from "@/components/atoms/loading-spinner";
import { useAuth } from "@/hooks/use-auth";

interface RouteGuardProps {
  children: React.ReactNode;
  requiredRole?: "user" | "admin" | "expert";
  fallback?: React.ReactNode;
}

export function RouteGuard({
  children,
  requiredRole,
  fallback,
}: RouteGuardProps) {
  const { user, isLoading, hasRole } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading) {
      // Check if user is authenticated
      if (!user) {
        // Redirect to login if not authenticated
        router.push("/login?redirect=" + encodeURIComponent(pathname));
        return;
      }

      // Check role-based access
      if (requiredRole && !hasRole(requiredRole)) {
        // Redirect to unauthorized page
        router.push("/unauthorized");
        return;
      }
    }
  }, [user, isLoading, requiredRole, router, pathname, hasRole]);

  // Show loading spinner while checking auth
  if (isLoading) {
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
  if (requiredRole && !hasRole(requiredRole)) {
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
