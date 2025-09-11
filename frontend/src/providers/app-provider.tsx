"use client";

import React, { createContext, useContext } from "react";
import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ErrorBoundary } from "@/components/error-boundary";
// import { StateProvider } from "@/components/state-provider";
import { CollaborationProvider } from "@/providers/collaboration-provider";
import { Toaster } from "@/ui/ui/toaster";
import { Analytics } from "@/ui/Analytics";

// Import performance utilities
import { performanceMonitor, usePerformanceTracking } from "@/lib/performance";

// Fallback error monitor
const errorMonitor = { addBreadcrumb: () => {}, captureError: () => {} };

// Enhanced React Query client with MAANG-level configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
             refetchOnWindowFocus: false,
       refetchOnReconnect: true,
    },
         mutations: {
       retry: 1,
     },
  },
});

interface AppContextType {
  // Add any global app state here
  isInitialized: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}

// Performance tracking wrapper
function PerformanceWrapper({ children }: { children: ReactNode }) {
  const { trackInteraction } = usePerformanceTracking('App');

  React.useEffect(() => {
    // Track app initialization
    performanceMonitor.markStart('AppInitialization');
    
    // Initialize performance monitoring
    if (typeof window !== 'undefined') {
      const handleLoad = () => {
        performanceMonitor.markEnd('AppInitialization');
      };

      if (document.readyState === 'complete') {
        handleLoad();
      } else {
        window.addEventListener('load', handleLoad);
        return () => window.removeEventListener('load', handleLoad);
      }
    }
    
    // Return empty cleanup function for cases where window is undefined
    return () => {};
  }, []);

  // Track user interactions globally
  React.useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const elementType = target.tagName.toLowerCase();
      
      // Only track interactive elements
      if (['button', 'a', 'input', 'select', 'textarea'].includes(elementType) || 
          target.closest('button, a, [role="button"]')) {
        const finishTracking = trackInteraction(`${elementType}_click`, target);
        setTimeout(finishTracking, 100);
      }
    };

    document.addEventListener('click', handleClick, { passive: true });
    return () => document.removeEventListener('click', handleClick);
  }, [trackInteraction]);

  return <>{children}</>;
}

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [isInitialized, setIsInitialized] = React.useState(false);

  React.useEffect(() => {
    // Initialize app
    setIsInitialized(true);
    
    // Initialize error monitoring
    errorMonitor.addBreadcrumb('App initialized', 'lifecycle', 'info');
  }, []);

  const contextValue: AppContextType = {
    isInitialized,
  };

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('App-level error:', error, errorInfo);
      }}
    >
      <QueryClientProvider client={queryClient}>
        <CollaborationProvider>
          <AppContext.Provider value={contextValue}>
            <div>
              <PerformanceWrapper>
                {children}
              </PerformanceWrapper>
              
              {/* Global UI Components */}
              <Toaster />
              <Analytics />
              
              {/* Development Tools */}
              {process.env.NODE_ENV === 'development' && (
                <DevelopmentTools />
              )}
            </div>
          </AppContext.Provider>
        </CollaborationProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

// Development tools component
function DevelopmentTools() {
  const [showDevTools, setShowDevTools] = React.useState(false);

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Toggle dev tools with Ctrl+Shift+D
      if (event.ctrlKey && event.shiftKey && event.key === 'D') {
        setShowDevTools(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!showDevTools) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setShowDevTools(true)}
          className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg"
          title="Press Ctrl+Shift+D to toggle"
        >
          🛠️ Dev
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 max-w-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
          Development Tools
        </h3>
        <button
          onClick={() => setShowDevTools(false)}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          ✕
        </button>
      </div>
      
      <div className="space-y-2 text-xs">
        <DevToolsStats />
        <DevToolsActions />
      </div>
    </div>
  );
}

// Development tools statistics
function DevToolsStats() {
  const [stats, setStats] = React.useState<any>(null);

  React.useEffect(() => {
    const interval = setInterval(() => {
      const perfStats = performanceMonitor.getMetrics();
      setStats(perfStats);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!stats) return null;

  return (
    <div className="space-y-1">
      <div className="text-gray-600 dark:text-gray-400">Performance:</div>
      <div className="pl-2 space-y-1">
        <div>Memory: {Math.round(((performance as any).memory?.usedJSHeapSize || 0) / 1024 / 1024)}MB</div>
        <div>URL: {stats.url?.split('?')[0] || 'N/A'}</div>
        <div>Session: {stats.sessionId?.slice(-8) || 'N/A'}</div>
      </div>
    </div>
  );
}

// Development tools actions
function DevToolsActions() {
  const clearCache = () => {
    if (confirm('Clear all cache data?')) {
      localStorage.clear();
      sessionStorage.clear();
      queryClient.clear();
      location.reload();
    }
  };

  const exportLogs = () => {
    const logs = {
      performance: performanceMonitor.getMetrics(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sarvanom-logs-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-2">
      <button
        onClick={clearCache}
        className="w-full text-left px-2 py-1 text-xs bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 rounded"
      >
        Clear Cache
      </button>
      <button
        onClick={exportLogs}
        className="w-full text-left px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 rounded"
      >
        Export Logs
      </button>
      <button
        onClick={() => window.open('/api/health', '_blank')}
        className="w-full text-left px-2 py-1 text-xs bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800 rounded"
      >
        API Health
      </button>
    </div>
  );
}
