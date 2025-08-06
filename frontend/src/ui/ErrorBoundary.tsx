"use client";

import React from "react";
import { ErrorBoundary as ReactErrorBoundary } from "react-error-boundary";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { AlertTriangle, RefreshCw, Home, AlertCircle } from "lucide-react";

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
  componentStack?: string;
}

function ErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  const [isClient, setIsClient] = React.useState(false);

  React.useEffect(() => {
    setIsClient(true);
  }, []);

  const handleReset = () => {
    resetErrorBoundary();
    if (isClient && typeof window !== "undefined") {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    if (isClient && typeof window !== "undefined") {
      window.location.href = "/";
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>
          <CardTitle className="text-xl">Something went wrong</CardTitle>
          <CardDescription>
            We encountered an unexpected error. Please try again or contact
            support if the problem persists.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {process.env.NODE_ENV === "development" && (
            <details className="rounded-md bg-muted p-3 text-sm">
              <summary className="cursor-pointer font-medium">
                Error Details
              </summary>
              <pre className="mt-2 whitespace-pre-wrap text-xs">
                {error.message}
                {error.stack && `\n\n${error.stack}`}
              </pre>
            </details>
          )}
          <div className="flex flex-col space-y-2 sm:flex-row sm:space-x-2 sm:space-y-0">
            <Button onClick={handleReset} className="flex-1">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
            <Button variant="outline" onClick={handleGoHome} className="flex-1">
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
  onError?: (error: Error, errorInfo: any) => void;
}

export function ErrorBoundary({ 
  children, 
  fallback = ErrorFallback,
  onError
}: ErrorBoundaryProps) {
  const handleError = (error: Error, errorInfo: any) => {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    
    // Send error to analytics
    try {
      // analytics.track('error', { error: error.message, stack: error.stack });
    } catch (analyticsError) {
      console.error("Failed to send error to analytics:", analyticsError);
    }

    onError?.(error, errorInfo);
  };

  return (
    <ReactErrorBoundary
      FallbackComponent={fallback}
      onError={handleError}
    >
      {children}
    </ReactErrorBoundary>
  );
}

// Specialized error boundaries for different contexts
export function QueryErrorBoundary({ children }: { children: React.ReactNode }) {
  const QueryErrorFallback = ({ error, resetErrorBoundary }: ErrorFallbackProps) => (
    <div className="p-6 border rounded-lg bg-red-50">
      <div className="flex items-center space-x-2 mb-4">
        <AlertCircle className="h-5 w-5 text-red-500" />
        <h3 className="font-medium text-red-800">Query Error</h3>
      </div>
      <p className="text-sm text-red-700 mb-4">
        There was an error processing your query. Please try again.
      </p>
      <Button onClick={resetErrorBoundary} size="sm">
        <RefreshCw className="mr-2 h-4 w-4" />
        Retry Query
      </Button>
    </div>
  );

  return (
    <ErrorBoundary fallback={QueryErrorFallback}>
      {children}
    </ErrorBoundary>
  );
}

export function AnalyticsErrorBoundary({ children }: { children: React.ReactNode }) {
  const AnalyticsErrorFallback = ({ error, resetErrorBoundary }: ErrorFallbackProps) => (
    <div className="p-6 border rounded-lg bg-yellow-50">
      <div className="flex items-center space-x-2 mb-4">
        <AlertCircle className="h-5 w-5 text-yellow-500" />
        <h3 className="font-medium text-yellow-800">Analytics Error</h3>
      </div>
      <p className="text-sm text-yellow-700 mb-4">
        Unable to load analytics data. Please refresh the page.
      </p>
      <Button onClick={resetErrorBoundary} size="sm" variant="outline">
        <RefreshCw className="mr-2 h-4 w-4" />
        Refresh Data
      </Button>
    </div>
  );

  return (
    <ErrorBoundary fallback={AnalyticsErrorFallback}>
      {children}
    </ErrorBoundary>
  );
}

// Hook for functional components to handle errors
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((error: Error) => {
    console.error("Error caught by useErrorHandler:", error);
    setError(error);

    // Send error to analytics
    try {
      // analytics.track('error', { error: error.message, stack: error.stack });
    } catch (analyticsError) {
      console.error("Failed to send error to analytics:", analyticsError);
    }
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
}
