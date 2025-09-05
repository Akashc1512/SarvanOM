"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home, MessageCircle } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { useToast } from "@/hooks/useToast";
import Link from "next/link";

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  traceId: string | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      traceId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Generate a trace ID for this error
    const traceId = `frontend-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      traceId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    
    // Update state with error info
    this.setState({ errorInfo });
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // Log to external service (in a real app, you'd send this to your logging service)
    this.logErrorToService(error, errorInfo);
  }

  private logErrorToService(error: Error, errorInfo: ErrorInfo) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      traceId: this.state.traceId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // In a real implementation, you'd send this to your logging service
    // For now, we'll just log it to console
    console.error("Error logged:", errorData);
    
    // You could also send to your backend API
    // fetch('/api/log-error', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(errorData)
    // }).catch(console.error);
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      traceId: null,
    });
  };

  private handleGoHome = () => {
    window.location.href = "/";
  };

  private copyTraceId = () => {
    if (this.state.traceId) {
      navigator.clipboard.writeText(this.state.traceId);
      // You could show a toast here
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return <ErrorFallback 
        error={this.state.error}
        errorInfo={this.state.errorInfo}
        traceId={this.state.traceId}
        onRetry={this.handleRetry}
        onGoHome={this.handleGoHome}
        onCopyTraceId={this.copyTraceId}
      />;
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  traceId: string | null;
  onRetry: () => void;
  onGoHome: () => void;
  onCopyTraceId: () => void;
}

function ErrorFallback({
  error,
  errorInfo,
  traceId,
  onRetry,
  onGoHome,
  onCopyTraceId,
}: ErrorFallbackProps) {
  const { toast } = useToast();

  const handleCopyTraceId = () => {
    onCopyTraceId();
    toast({
      title: "Trace ID copied",
      description: "Trace ID copied to clipboard for support",
      variant: "default",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-red-50 to-orange-50 dark:from-slate-900 dark:via-red-900/20 dark:to-orange-900/20 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-red-200/50 dark:border-red-800/50">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <CardTitle className="text-2xl font-bold text-red-600 dark:text-red-400">
            Something went wrong
          </CardTitle>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            We encountered an unexpected error. Don't worry, our team has been notified.
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Error Details */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Error Details
              </h3>
              <Badge variant="destructive" className="text-xs">
                {error?.name || "Unknown Error"}
              </Badge>
            </div>
            
            {error && (
              <div className="bg-gray-50 dark:bg-slate-700/50 rounded-lg p-4">
                <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                  {error.message}
                </p>
              </div>
            )}
          </div>

          {/* Trace ID */}
          {traceId && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900 dark:text-white">
                Trace ID
              </h4>
              <div className="flex items-center space-x-2">
                <code className="flex-1 bg-gray-50 dark:bg-slate-700/50 rounded px-3 py-2 text-sm font-mono text-gray-700 dark:text-gray-300">
                  {traceId}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyTraceId}
                  className="shrink-0"
                >
                  Copy
                </Button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Please include this trace ID when contacting support
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button
              onClick={onRetry}
              className="flex-1 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            
            <Button
              variant="outline"
              onClick={onGoHome}
              className="flex-1"
            >
              <Home className="w-4 h-4 mr-2" />
              Go Home
            </Button>
          </div>

          {/* Support */}
          <div className="border-t border-gray-200 dark:border-slate-600 pt-4">
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <MessageCircle className="w-4 h-4" />
              <span>Need help?</span>
              <Link
                href="/support"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                Contact Support
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Hook for functional components to trigger error boundary
export function useErrorHandler() {
  const throwError = (error: Error) => {
    throw error;
  };

  return { throwError };
}

// Higher-order component for error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

// Specific error boundary for search results
export function SearchErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Search Error
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            We encountered an error while processing your search. Please try again.
          </p>
          <Button onClick={() => window.location.reload()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry Search
          </Button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

// Specific error boundary for streaming
export function StreamingErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            <span className="text-sm text-yellow-800 dark:text-yellow-200">
              Streaming interrupted. Please refresh to continue.
            </span>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

// Specific error boundary for query operations
export function QueryErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="p-6 text-center cosmic-card">
          <AlertTriangle className="w-12 h-12 text-cosmic-warning mx-auto mb-4" />
          <h3 className="text-lg font-semibold cosmic-text-primary mb-2">
            Query Error
          </h3>
          <p className="cosmic-text-secondary mb-4">
            We encountered an error while processing your query. Please try again.
          </p>
          <Button onClick={() => window.location.reload()} className="cosmic-btn-primary">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry Query
          </Button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}