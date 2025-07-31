import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { api, type QueryResponse, type QueryRequest } from "@/lib/api";

interface QueryState {
  // State
  currentQuery: QueryResponse | null;
  recentQueries: QueryResponse[];
  isSubmitting: boolean;
  isPolling: boolean;
  error: string | null;

  // Actions
  submitQuery: (request: QueryRequest) => Promise<void>;
  updateQuery: (query: QueryResponse) => void;
  setCurrentQuery: (query: QueryResponse | null) => void;
  addToRecentQueries: (query: QueryResponse) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  currentQuery: null,
  recentQueries: [],
  isSubmitting: false,
  isPolling: false,
  error: null,
};

export const useQueryStore = create<QueryState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        submitQuery: async (request: QueryRequest) => {
          set({ isSubmitting: true, error: null });

          try {
            const response = await api.submitQuery(request);
            set({
              currentQuery: response,
              isSubmitting: false,
              isPolling: true,
            });

            // Add to recent queries
            get().addToRecentQueries(response);
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || "Failed to submit query",
              isSubmitting: false,
            });
            throw error;
          }
        },

        updateQuery: (query: QueryResponse) => {
          set({ currentQuery: query });

          // Update in recent queries
          set((state) => ({
            recentQueries: state.recentQueries.map((q) =>
              q.query_id === query.query_id ? query : q,
            ),
          }));

          // Stop polling if completed or failed
          if (query.status === "completed" || query.status === "failed") {
            set({ isPolling: false });
          }
        },

        setCurrentQuery: (query: QueryResponse | null) => {
          set({ currentQuery: query });
        },

        addToRecentQueries: (query: QueryResponse) => {
          set((state) => ({
            recentQueries: [query, ...state.recentQueries.slice(0, 4)],
          }));
        },

        clearError: () => {
          set({ error: null });
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: "query-store",
        partialize: (state) => ({
          recentQueries: state.recentQueries,
        }),
      },
    ),
    {
      name: "query-store",
    },
  ),
);
