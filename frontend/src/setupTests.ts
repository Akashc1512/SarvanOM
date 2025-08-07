/**
 * Jest Test Setup Configuration
 * This file is run before each test file
 */

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, jest } from '@jest/globals';

// Cleanup after each test
afterEach(() => {
  cleanup();
  jest.clearAllMocks();
  jest.clearAllTimers();
  localStorage.clear();
  sessionStorage.clear();
});

// Setup before each test
beforeEach(() => {
  // Reset all mocks
  jest.resetModules();
  
  // Mock console methods to reduce noise in tests
  jest.spyOn(console, 'error').mockImplementation(() => {});
  jest.spyOn(console, 'warn').mockImplementation(() => {});
  jest.spyOn(console, 'log').mockImplementation(() => {});
  
  // Mock fetch globally
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      headers: new Headers(),
      redirected: false,
      statusText: 'OK',
      type: 'basic',
      url: '',
      clone: jest.fn(),
      body: null,
      bodyUsed: false,
      arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
      blob: () => Promise.resolve(new Blob()),
      formData: () => Promise.resolve(new FormData()),
    } as Response)
  );
});

// Global test utilities
global.testUtils = {
  // Create a mock user event
  createMockUser: () => ({
    id: 'test-user-id',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user' as const,
    preferences: {
      theme: 'light' as const,
      language: 'en',
      notifications: true,
    },
  }),

  // Create mock query response
  createMockQueryResponse: () => ({
    query_id: 'test-query-id',
    answer: 'Test answer',
    sources: [],
    timestamp: new Date().toISOString(),
    processing_time: 1000,
    confidence_score: 0.95,
  }),

  // Create mock analytics data
  createMockAnalyticsData: () => ({
    totalQueries: 100,
    averageResponseTime: 1500,
    successRate: 0.95,
    topQueries: [
      { query: 'test query 1', count: 10 },
      { query: 'test query 2', count: 8 },
    ],
    dailyStats: [
      { date: '2024-01-01', queries: 25, responseTime: 1400 },
      { date: '2024-01-02', queries: 30, responseTime: 1600 },
    ],
  }),

  // Wait for async operations
  waitFor: async (ms = 0) => new Promise(resolve => setTimeout(resolve, ms)),

  // Mock timers
  mockTimers: () => {
    jest.useFakeTimers();
  },

  restoreTimers: () => {
    jest.useRealTimers();
  },
};

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000';

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />;
  },
}));

// Mock Next.js Link component
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...props }: any) => {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  },
}));

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    section: ({ children, ...props }: any) => <section {...props}>{children}</section>,
  },
  AnimatePresence: ({ children }: any) => children,
  useAnimation: () => ({
    start: jest.fn(),
    stop: jest.fn(),
    set: jest.fn(),
  }),
  useInView: () => [jest.fn(), true],
}));

// Mock React Query
jest.mock('@tanstack/react-query', () => ({
  useQuery: () => ({
    data: null,
    error: null,
    isLoading: false,
    isError: false,
    isSuccess: true,
    refetch: jest.fn(),
  }),
  useMutation: () => ({
    mutate: jest.fn(),
    mutateAsync: jest.fn(),
    isLoading: false,
    isError: false,
    isSuccess: true,
    error: null,
    data: null,
  }),
  QueryClient: jest.fn().mockImplementation(() => ({
    invalidateQueries: jest.fn(),
    setQueryData: jest.fn(),
    getQueryData: jest.fn(),
    clear: jest.fn(),
  })),
  QueryClientProvider: ({ children }: any) => children,
  ReactQueryDevtools: () => null,
}));

// Mock Zustand
jest.mock('zustand', () => ({
  create: () => () => ({
    user: null,
    isAuthenticated: false,
    setUser: jest.fn(),
    logout: jest.fn(),
  }),
}));

// Custom matchers
expect.extend({
  toBeInTheDocument: (received) => {
    const pass = received != null;
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be in the document`,
      pass,
    };
  },
});

// Extend global types
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
    }
  }

  var testUtils: {
    createMockUser: () => any;
    createMockQueryResponse: () => any;
    createMockAnalyticsData: () => any;
    waitFor: (ms?: number) => Promise<void>;
    mockTimers: () => void;
    restoreTimers: () => void;
  };
}