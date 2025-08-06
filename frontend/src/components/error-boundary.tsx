"use client";

import * as React from 'react';
import { ErrorInfo } from 'react';
import { 
  errorMonitor, 
  ErrorSeverity, 
  ErrorCategory, 
  ErrorBoundaryConfig 
} from '@/lib/error-monitoring';

// Error Boundary State
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorId: string | null;
}

// Error Boundary Props
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; errorId: string; retry: () => void }>;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

// React Error Boundary Component
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorId: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorId: null, // Will be set in componentDidCatch
    };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const context: any = {
      severity: ErrorSeverity.HIGH,
      category: ErrorCategory.RENDER,
      errorBoundary: this.constructor.name,
    };
    
    if (errorInfo.componentStack) {
      context.componentStack = errorInfo.componentStack;
    }
    
    const errorId = errorMonitor.captureError(error, context);

    this.setState({ errorId });

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  private retry = () => {
    this.setState({ hasError: false, error: null, errorId: null });
  };

  override render() {
    if (this.state.hasError && this.state.error && this.state.errorId) {
      if (this.props.fallback) {
        return (
          <this.props.fallback
            error={this.state.error}
            errorId={this.state.errorId}
            retry={this.retry}
          />
        );
      }

      return (
        <DefaultErrorFallback
          error={this.state.error}
          errorId={this.state.errorId}
          retry={this.retry}
        />
      );
    }

    return this.props.children;
  }
}

// Default Error Fallback Component
function DefaultErrorFallback({ 
  error, 
  errorId, 
  retry 
}: { 
  error: Error; 
  errorId: string; 
  retry: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            <svg 
              className="h-6 w-6 text-red-400" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-gray-900">
              Something went wrong
            </h3>
          </div>
        </div>
        
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            We&apos;re sorry, but something unexpected happened. The error has been logged and our team has been notified.
          </p>
        </div>

        {process.env.NODE_ENV === 'development' && (
          <div className="mb-4 p-3 bg-red-50 rounded-md">
            <p className="text-xs font-mono text-red-700">{error.message}</p>
            <p className="text-xs text-red-500 mt-1">Error ID: {errorId}</p>
          </div>
        )}

        <div className="flex space-x-3">
          <button
            onClick={retry}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="flex-1 bg-gray-200 text-gray-900 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );
}

// HOC for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: ErrorBoundaryConfig
) {
  return function WrappedComponent(props: P) {
    const errorBoundaryOnlyProps: Pick<ErrorBoundaryProps, 'fallback' | 'onError'> = {};
    
    if (errorBoundaryProps?.fallback) {
      errorBoundaryOnlyProps.fallback = errorBoundaryProps.fallback;
    }
    
    if (errorBoundaryProps?.onError) {
      errorBoundaryOnlyProps.onError = errorBoundaryProps.onError;
    }
    
    return (
      <ErrorBoundary {...errorBoundaryOnlyProps}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}