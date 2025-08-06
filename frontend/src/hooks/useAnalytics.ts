import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";

interface AnalyticsData {
  total_queries: number;
  expert_validations: number;
  average_response_time: number;
  time_saved_per_query: number;
  top_topics: Array<{ topic: string; count: number }>;
  queries_over_time: Array<{ date: string; count: number }>;
  validations_over_time: Array<{ date: string; count: number }>;
  recent_activity: Array<{
    id: string;
    type: "query" | "validation" | "feedback";
    description: string;
    timestamp: string;
    user_id?: string;
  }>;
}

interface UseAnalyticsOptions {
  timeRange?: "7d" | "30d" | "90d";
  enabled?: boolean;
}

export function useAnalytics({ timeRange = "30d", enabled = true }: UseAnalyticsOptions = {}) {
  return useQuery({
    queryKey: ["analytics", timeRange],
    queryFn: async (): Promise<AnalyticsData> => {
      const response = await fetch(`/api/analytics/summary?time_range=${timeRange}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analytics: ${response.statusText}`);
      }
      
      return response.json();
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: async () => {
      const response = await fetch("/api/analytics/summary");
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analytics summary: ${response.statusText}`);
      }
      
      return response.json();
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
} 