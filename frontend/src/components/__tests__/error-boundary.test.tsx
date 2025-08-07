/**
 * Error Boundary Component Tests
 * Comprehensive test suite for the ErrorBoundary component
 */

import React from 'react';
import { renderWithProviders, screen, waitFor } from '@/__tests__/utils/test-utils';
import { ErrorBoundary, withErrorBoundary } from '../error-boundary';
import { errorMonitor } from '@/lib/error-monitoring';

// Mock the error monitoring
jest.mock('@/lib/error-monitoring', () => ({
  errorMonitor: {
    captureError: jest.fn(() => 'mock-error-id'),
  },
  ErrorSeverity: {
    HIGH: 'high',
  },
  ErrorCategory: {
    RENDER: 'render',
  },
}));

// Component that throws an error for testing
const ThrowError = ({ shouldThrow = false }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that throws an error conditionally
const ConditionalError = ({ errorMessage }: { errorMessage?: string }) => {
  if (errorMessage) {
    throw new Error(errorMessage);
  }
  return <div data-testid="success">Success</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console.error for these tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Normal Operation', () => {
    it('should render children when no error occurs', () => {
      renderWithProviders(
        <ErrorBoundary>
          <div data-testid="child">Child content</div>
        </ErrorBoundary>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Child content')).toBeInTheDocument();
    });

    it('should not call error monitoring when no error occurs', () => {
      renderWithProviders(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(errorMonitor.captureError).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should catch and display error with default fallback', () => {
      renderWithProviders(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText(/We're sorry, but something unexpected happened/)).toBeInTheDocument();
    });

    it('should call error monitoring when error occurs', () => {
      renderWithProviders(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(errorMonitor.captureError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          severity: 'high',
          category: 'render',
          errorBoundary: 'ErrorBoundary',
        })
      );
    });

    it('should display error message in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      renderWithProviders(
        <ErrorBoundary>
          <ConditionalError errorMessage="Custom error message" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom error message')).toBeInTheDocument();
      expect(screen.getByText(/Error ID:/)).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not display error details in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      renderWithProviders(
        <ErrorBoundary>
          <ConditionalError errorMessage="Custom error message" />
        </ErrorBoundary>
      );

      expect(screen.queryByText('Custom error message')).not.toBeInTheDocument();
      expect(screen.queryByText(/Error ID:/)).not.toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Custom Fallback', () => {
    const CustomFallback = ({ error, errorId, retry }: any) => (
      <div>
        <h2>Custom Error</h2>
        <p data-testid="error-message">{error.message}</p>
        <p data-testid="error-id">{errorId}</p>
        <button onClick={retry} data-testid="custom-retry">
          Custom Retry
        </button>
      </div>
    );

    it('should render custom fallback when provided', () => {
      renderWithProviders(
        <ErrorBoundary fallback={CustomFallback}>
          <ConditionalError errorMessage="Custom error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error')).toBeInTheDocument();
      expect(screen.getByTestId('error-message')).toHaveTextContent('Custom error');
      expect(screen.getByTestId('error-id')).toHaveTextContent('mock-error-id');
      expect(screen.getByTestId('custom-retry')).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('should allow retry with Try Again button', async () => {
      const { user } = renderWithProviders(
        <ErrorBoundary>
          <ConditionalError errorMessage="Recoverable error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      const retryButton = screen.getByText('Try Again');
      await user.click(retryButton);

      // After retry, the component should render normally
      await waitFor(() => {
        expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
      });
    });

    it('should reload page with Reload Page button', async () => {
      const mockReload = jest.fn();
      Object.defineProperty(window, 'location', {
        value: { reload: mockReload },
        writable: true,
      });

      const { user } = renderWithProviders(
        <ErrorBoundary>
          <ConditionalError errorMessage="Fatal error" />
        </ErrorBoundary>
      );

      const reloadButton = screen.getByText('Reload Page');
      await user.click(reloadButton);

      expect(mockReload).toHaveBeenCalled();
    });
  });

  describe('onError Callback', () => {
    it('should call onError callback when error occurs', () => {
      const onErrorMock = jest.fn();

      renderWithProviders(
        <ErrorBoundary onError={onErrorMock}>
          <ConditionalError errorMessage="Callback test error" />
        </ErrorBoundary>
      );

      expect(onErrorMock).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });
  });
});

describe('withErrorBoundary HOC', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should wrap component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(ThrowError);

    renderWithProviders(<WrappedComponent shouldThrow={false} />);

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('should catch errors in wrapped component', () => {
    const WrappedComponent = withErrorBoundary(ThrowError);

    renderWithProviders(<WrappedComponent shouldThrow={true} />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should pass through props to wrapped component', () => {
    const TestComponent = ({ testProp }: { testProp: string }) => (
      <div data-testid="test-prop">{testProp}</div>
    );

    const WrappedComponent = withErrorBoundary(TestComponent);

    renderWithProviders(<WrappedComponent testProp="test value" />);

    expect(screen.getByTestId('test-prop')).toHaveTextContent('test value');
  });

  it('should use custom fallback when provided', () => {
    const CustomFallback = () => <div>Custom HOC Fallback</div>;
    const WrappedComponent = withErrorBoundary(ThrowError, {
      fallback: CustomFallback,
    });

    renderWithProviders(<WrappedComponent shouldThrow={true} />);

    expect(screen.getByText('Custom HOC Fallback')).toBeInTheDocument();
  });
});

describe('Error Boundary Performance', () => {
  it('should not affect render performance when no error occurs', async () => {
    const startTime = performance.now();

    renderWithProviders(
      <ErrorBoundary>
        <div>Performance test</div>
      </ErrorBoundary>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render quickly (less than 100ms in test environment)
    expect(renderTime).toBeLessThan(100);
  });

  it('should handle multiple children efficiently', () => {
    const children = Array.from({ length: 100 }, (_, i) => (
      <div key={i}>Child {i}</div>
    ));

    renderWithProviders(<ErrorBoundary>{children}</ErrorBoundary>);

    expect(screen.getByText('Child 0')).toBeInTheDocument();
    expect(screen.getByText('Child 99')).toBeInTheDocument();
  });
});