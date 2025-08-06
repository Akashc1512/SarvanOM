"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Button } from "@/ui/ui/button";
import { Skeleton } from "@/ui/ui/skeleton";
import { 
  BarChart3, 
  LineChart, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  Users, 
  Activity,
  RefreshCw,
  AlertCircle,
  Calendar,
  Target,
  Zap
} from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { AnalyticsDashboard } from "@/ui/AnalyticsDashboard";
import { ErrorBoundary } from "@/ui/ErrorBoundary";

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

export default function AnalyticsPage() {
  const { toast } = useToast();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "90d">("30d");

  const fetchAnalyticsData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/analytics/summary?time_range=${timeRange}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch analytics: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalyticsData(data);
    } catch (error) {
      console.error("Error fetching analytics:", error);
      setError(error instanceof Error ? error.message : "Failed to fetch analytics data");
      toast({
        title: "Analytics Loading Failed",
        description: "Failed to load analytics data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const handleTimeRangeChange = (range: "7d" | "30d" | "90d") => {
    setTimeRange(range);
  };

  const handleRefresh = () => {
    fetchAnalyticsData();
  };

  return (
    <ErrorBoundary>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <AnalyticsDashboard
            data={analyticsData || undefined}
            isLoading={isLoading}
            error={error}
            timeRange={timeRange}
            onTimeRangeChange={handleTimeRangeChange}
            onRefresh={handleRefresh}
          />
        </div>
      </div>
    </ErrorBoundary>
  );
} 