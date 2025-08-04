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
      const response = await fetch(`/analytics/summary?time_range=${timeRange}`);
      
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

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatResponseTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (error && !analyticsData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Failed to Load Analytics
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={fetchAnalyticsData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">
              Track your platform usage and performance metrics
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={fetchAnalyticsData}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <div className="flex border rounded-lg">
              {(["7d", "30d", "90d"] as const).map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setTimeRange(range)}
                  className="rounded-none first:rounded-l-lg last:rounded-r-lg"
                >
                  {range}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Queries */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {analyticsData?.total_queries?.toLocaleString() || "0"}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              +12% from last period
            </p>
          </CardContent>
        </Card>

        {/* Expert Validations */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expert Validations</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {analyticsData?.expert_validations?.toLocaleString() || "0"}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              +8% from last period
            </p>
          </CardContent>
        </Card>

        {/* Average Response Time */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {analyticsData?.average_response_time 
                  ? formatResponseTime(analyticsData.average_response_time)
                  : "0ms"
                }
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              -5% from last period
            </p>
          </CardContent>
        </Card>

        {/* Time Saved */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-2xl font-bold">
                {analyticsData?.time_saved_per_query 
                  ? formatTime(analyticsData.time_saved_per_query)
                  : "0 min"
                }
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              per query on average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="mb-8">
        <AnalyticsDashboard
          queriesOverTime={analyticsData?.queries_over_time || []}
          validationsOverTime={analyticsData?.validations_over_time || []}
          topTopics={analyticsData?.top_topics || []}
          isLoading={isLoading}
        />
      </div>

      {/* Top Topics */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Top Queried Topics
          </CardTitle>
          <CardDescription>
            Most frequently asked topics in the selected time period
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {analyticsData?.top_topics?.slice(0, 10).map((topic, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <Badge variant="secondary">{index + 1}</Badge>
                    <span className="font-medium">{topic.topic}</span>
                  </div>
                  <Badge variant="outline">{topic.count} queries</Badge>
                </div>
              ))}
              {(!analyticsData?.top_topics || analyticsData.top_topics.length === 0) && (
                <div className="text-center text-gray-500 py-8">
                  No topic data available for the selected time period
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
          <CardDescription>
            Latest queries, validations, and feedback from users
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-3 border rounded-lg">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-full mb-2" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {analyticsData?.recent_activity?.slice(0, 10).map((activity, index) => (
                <div key={activity.id} className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="flex-shrink-0">
                    {activity.type === "query" && <BarChart3 className="h-5 w-5 text-blue-500" />}
                    {activity.type === "validation" && <CheckCircle className="h-5 w-5 text-green-500" />}
                    {activity.type === "feedback" && <Users className="h-5 w-5 text-purple-500" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {activity.description}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {activity.type}
                  </Badge>
                </div>
              ))}
              {(!analyticsData?.recent_activity || analyticsData.recent_activity.length === 0) && (
                <div className="text-center text-gray-500 py-8">
                  No recent activity available
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 