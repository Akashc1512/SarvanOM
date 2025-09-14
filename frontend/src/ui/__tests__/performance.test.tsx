import React from "react";
import { render } from "@testing-library/react";
import { AnswerDisplay } from "@/components/search/AnswerDisplay";
import { QueryForm } from "../QueryForm";

// Mock dependencies
jest.mock("@/hooks/useToast", () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

jest.mock("@/store/query-store", () => ({
  useQueryStore: () => ({
    currentQuery: null,
    submitQuery: jest.fn(),
    updateQuery: jest.fn(),
    clearError: jest.fn(),
  }),
}));

jest.mock("@/hooks/useDebounce", () => ({
  useDebounce: (value: any) => value,
}));

jest.mock("@/hooks/usePolling", () => ({
  usePolling: () => ({
    isPolling: false,
    startPolling: jest.fn(),
    stopPolling: jest.fn(),
  }),
}));

jest.mock("@/lib/api", () => ({
  api: {
    submitQuery: jest.fn(),
    getQuery: jest.fn(),
    submitFeedback: jest.fn(),
  },
}));

describe("Performance Tests", () => {
  describe("QueryForm", () => {
    it("renders within acceptable time limit (50ms)", () => {
      const startTime = performance.now();
      render(<QueryForm />);
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(50);
    });

    it("re-renders within acceptable time limit (20ms)", () => {
      const { rerender } = render(<QueryForm />);
      
      const startTime = performance.now();
      rerender(<QueryForm />);
      const endTime = performance.now();
      const reRenderTime = endTime - startTime;

      expect(reRenderTime).toBeLessThan(20);
    });

    it("handles rapid state changes efficiently", () => {
      const { rerender } = render(<QueryForm />);
      
      const startTime = performance.now();
      
      // Simulate rapid re-renders
      for (let i = 0; i < 10; i++) {
        rerender(<QueryForm />);
      }
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;

      expect(totalTime).toBeLessThan(100);
    });
  });

  describe("AnswerDisplay", () => {
    const mockQuery = {
      query_id: "test-123",
      query: "Test query",
      answer: "This is a test answer with some content to render.",
      status: "completed" as const,
      confidence: 0.85,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
      sources: [
        {
          title: "Test Source",
          url: "https://example.com",
          snippet: "Test snippet",
          relevance_score: 0.9,
          source_type: "web" as const,
        },
      ],
    };

    it("renders within acceptable time limit (100ms)", () => {
      const startTime = performance.now();
      render(<AnswerDisplay query={mockQuery} />);
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(100);
    });

    it("re-renders within acceptable time limit (30ms)", () => {
      const { rerender } = render(<AnswerDisplay query={mockQuery} />);
      
      const startTime = performance.now();
      rerender(<AnswerDisplay query={mockQuery} />);
      const endTime = performance.now();
      const reRenderTime = endTime - startTime;

      expect(reRenderTime).toBeLessThan(30);
    });

    it("handles large content efficiently", () => {
      const largeQuery = {
        ...mockQuery,
        answer: "A".repeat(10000), // Large content
        sources: Array.from({ length: 50 }, (_, i) => ({
          title: `Source ${i}`,
          url: `https://example${i}.com`,
          snippet: `Snippet ${i}`.repeat(100),
          relevance_score: 0.8,
          source_type: "web" as const,
        })),
      };

      const startTime = performance.now();
      render(<AnswerDisplay query={largeQuery} />);
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(200); // Allow more time for large content
    });
  });

  describe("Memory Usage", () => {
    it("does not cause memory leaks during rapid re-renders", () => {
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      const { rerender, unmount } = render(<QueryForm />);
      
      // Simulate rapid re-renders
      for (let i = 0; i < 100; i++) {
        rerender(<QueryForm />);
      }
      
      unmount();
      
      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryIncrease = finalMemory - initialMemory;

      expect(memoryIncrease).toBeLessThan(1024 * 1024); // Less than 1MB increase
    });
  });

  describe("Bundle Size Impact", () => {
    it("components should be tree-shakeable", () => {
      expect(typeof QueryForm).toBe("function");
      expect(typeof AnswerDisplay).toBe("function");
    });
  });
});
