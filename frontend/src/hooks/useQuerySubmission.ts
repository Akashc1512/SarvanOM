import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { api, type QueryRequest, type QueryResponse } from "@/services/api";

interface UseQuerySubmissionOptions {
  onSuccess?: (data: QueryResponse) => void;
  onError?: (error: Error) => void;
}

export function useQuerySubmission(options: UseQuerySubmissionOptions = {}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (queryRequest: QueryRequest): Promise<QueryResponse> => {
      const response = await api.submitQuery(queryRequest);
      return response;
    },
    onSuccess: (data) => {
      // Invalidate and refetch queries list
      queryClient.invalidateQueries({ queryKey: ["queries"] });
      
      // Add to recent queries cache
      queryClient.setQueryData(["recent-queries"], (old: QueryResponse[] = []) => {
        return [data, ...old.slice(0, 9)]; // Keep last 10 queries
      });

      options.onSuccess?.(data);
    },
    onError: (error: Error) => {
      console.error("Query submission error:", error);
      options.onError?.(error);
    },
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 5000),
  });
}

export function useQueryPolling(queryId: string | null) {
  return useQuery({
    queryKey: ["query", queryId],
    queryFn: async (): Promise<QueryResponse> => {
      if (!queryId) throw new Error("No query ID provided");
      
      const response = await api.getQuery(queryId);
      return response as QueryResponse;
    },
    enabled: !!queryId,
    refetchInterval: (query) => {
      // Stop polling when query is complete
      const data = query.state.data;
      if (data?.status === "completed" || data?.status === "failed") {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    refetchIntervalInBackground: false,
    retry: false, // Don't retry failed queries
  });
} 