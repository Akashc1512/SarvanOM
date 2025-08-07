/**
 * Custom Test Utilities
 * Provides enhanced testing utilities for React components
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';
import userEvent from '@testing-library/user-event';

// Create a custom render function that includes providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[];
  user?: any;
  queryClient?: QueryClient;
  theme?: 'light' | 'dark' | 'system';
}

interface CustomRenderResult extends RenderResult {
  user: ReturnType<typeof userEvent.setup>;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    initialEntries = ['/'],
    user,
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    }),
    theme = 'light',
    ...renderOptions
  }: CustomRenderOptions = {}
): CustomRenderResult {
  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme={theme} enableSystem={false}>
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    );
  };

  const renderResult = render(ui, {
    wrapper: AllTheProviders,
    ...renderOptions,
  });

  return {
    user: user || userEvent.setup(),
    ...renderResult,
  };
}

// Custom hook testing utility
export function renderHook<TProps, TResult>(
  callback: (props: TProps) => TResult,
  options?: {
    initialProps?: TProps;
    wrapper?: React.ComponentType<{ children: React.ReactNode }>;
  }
) {
  const { initialProps, wrapper } = options || {};
  let result: { current: TResult };
  let rerender: (props?: TProps) => void;

  function TestComponent(props: TProps) {
    result = { current: callback(props) };
    return null;
  }

  const { rerender: rerenderComponent } = render(
    <TestComponent {...(initialProps as TProps)} />,
    { wrapper }
  );

  rerender = (newProps?: TProps) => {
    rerenderComponent(<TestComponent {...(newProps || initialProps as TProps)} />);
  };

  return {
    result: result!,
    rerender,
  };
}

// Mock API responses
export const mockApiResponse = {
  success: <T>(data: T) => ({
    ok: true,
    status: 200,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  }),

  error: (status: number, message: string) => ({
    ok: false,
    status,
    json: () => Promise.resolve({ error: message }),
    text: () => Promise.resolve(message),
  }),
};

// Performance testing utilities
export const performanceUtils = {
  measureRenderTime: async (renderFn: () => void) => {
    const start = performance.now();
    renderFn();
    const end = performance.now();
    return end - start;
  },

  measureAsyncOperation: async (operation: () => Promise<void>) => {
    const start = performance.now();
    await operation();
    const end = performance.now();
    return end - start;
  },
};

// Accessibility testing utilities
export const a11yUtils = {
  findByRole: (container: HTMLElement, role: string, options?: any) => {
    return container.querySelector(`[role="${role}"]`);
  },

  findByAriaLabel: (container: HTMLElement, label: string) => {
    return container.querySelector(`[aria-label="${label}"]`);
  },

  hasAriaAttribute: (element: Element, attribute: string) => {
    return element.hasAttribute(attribute);
  },
};

// Form testing utilities
export const formUtils = {
  fillInput: async (user: any, input: HTMLElement, value: string) => {
    await user.clear(input);
    await user.type(input, value);
  },

  selectOption: async (user: any, select: HTMLElement, value: string) => {
    await user.selectOptions(select, value);
  },

  submitForm: async (user: any, form: HTMLElement) => {
    await user.click(form.querySelector('[type="submit"]') || form);
  },
};

// Animation testing utilities
export const animationUtils = {
  skipAnimations: () => {
    const style = document.createElement('style');
    style.textContent = `
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-delay: 0.01ms !important;
        transition-duration: 0.01ms !important;
        transition-delay: 0.01ms !important;
        scroll-behavior: auto !important;
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  },
};

// Wait utilities
export const waitUtils = {
  waitForLoadingToFinish: async () => {
    const { findByTestId } = renderWithProviders(<div />);
    try {
      await findByTestId('loading-spinner', { timeout: 100 });
    } catch {
      // Loading spinner not found, which means loading is finished
    }
  },

  waitForElement: async (selector: string, timeout = 1000) => {
    return new Promise<Element>((resolve, reject) => {
      const startTime = Date.now();
      const checkForElement = () => {
        const element = document.querySelector(selector);
        if (element) {
          resolve(element);
        } else if (Date.now() - startTime > timeout) {
          reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        } else {
          setTimeout(checkForElement, 100);
        }
      };
      checkForElement();
    });
  },
};

// Mock data generators
export const mockData = {
  user: (overrides = {}) => ({
    id: 'user-1',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user',
    preferences: {
      theme: 'light',
      language: 'en',
      notifications: true,
    },
    ...overrides,
  }),

  query: (overrides = {}) => ({
    query_id: 'query-1',
    query: 'Test query',
    answer: 'Test answer',
    sources: [],
    timestamp: new Date().toISOString(),
    processing_time: 1000,
    confidence_score: 0.95,
    ...overrides,
  }),

  analytics: (overrides = {}) => ({
    totalQueries: 100,
    averageResponseTime: 1500,
    successRate: 0.95,
    topQueries: [
      { query: 'test query 1', count: 10 },
      { query: 'test query 2', count: 8 },
    ],
    dailyStats: [],
    ...overrides,
  }),
};

// Re-export everything from testing library
export * from '@testing-library/react';
export { userEvent };
export { default as userEvent } from '@testing-library/user-event';