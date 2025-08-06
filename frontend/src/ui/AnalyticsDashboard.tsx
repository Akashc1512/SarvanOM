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
  Zap,
  Loader2
} from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { LoadingSpinner } from "@/ui/atoms/loading-spinner";
import { AnalyticsSkeleton } from "@/ui/atoms/skeleton";
import { AnalyticsErrorBoundary } from "./ErrorBoundary";
import dynamic from "next/dynamic";

// Chart loading component with spinner
const ChartLoader = () => (
  <div className="h-64 flex items-center justify-center">
    <Loader2 className="h-6 w-6 animate-spin mr-2" />
    <span className="text-sm text-muted-foreground">Loading chart...</span>
  </div>
);

// Dynamically import chart components with proper loading states
const Line = dynamic(
  () => import("react-chartjs-2").then(mod => ({ default: mod.Line })),
  {
    ssr: false,
    loading: ChartLoader
  }
);

const Bar = dynamic(
  () => import("react-chartjs-2").then(mod => ({ default: mod.Bar })),
  {
    ssr: false,
    loading: ChartLoader
  }
);

const Doughnut = dynamic(
  () => import("react-chartjs-2").then(mod => ({ default: mod.Doughnut })),
  {
    ssr: false,
    loading: ChartLoader
  }
);

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

interface AnalyticsDashboardProps {
  data?: AnalyticsData | undefined;
  isLoading?: boolean;
  error?: string | null;
  timeRange?: "7d" | "30d" | "90d";
  onTimeRangeChange?: (range: "7d" | "30d" | "90d") => void;
  onRefresh?: () => void;
}

export function AnalyticsDashboard({
  data,
  isLoading = false,
  error = null,
  timeRange = "30d",
  onTimeRangeChange,
  onRefresh
}: AnalyticsDashboardProps) {
  const { toast } = useToast();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isLoading || !isClient) return;
    
    const initializeCharts = async () => {
      try {
        // Only initialize Chart.js if it hasn't been initialized yet
        const chartModule = await import("chart.js");
        const { Chart: ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } = chartModule;
        
        // Register only if not already registered
        if (!ChartJS.registry.getScale('category')) {
          ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);
        }
      } catch (error) {
        console.error("Failed to initialize charts:", error);
        toast({
          title: "Chart Initialization Failed",
          description: "Charts may not display properly. Please refresh the page.",
          variant: "destructive",
        });
      }
    };

    initializeCharts();
  }, [isLoading, isClient, toast]);

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

  // Show loading skeleton when loading
  if (isLoading) {
    return (
      <AnalyticsErrorBoundary>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <LoadingSpinner size="sm" variant="dots" />
              <span className="text-sm text-muted-foreground">
                Loading analytics data...
              </span>
            </div>
            <Button variant="outline" size="sm" disabled>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Loading...
            </Button>
          </div>
          <AnalyticsSkeleton />
        </div>
      </AnalyticsErrorBoundary>
    );
  }

  // Show error state
  if (error) {
    return (
      <AnalyticsErrorBoundary>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <span className="text-sm text-destructive">Failed to load analytics</span>
            </div>
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
          <Card className="border-destructive/50">
            <CardContent className="p-6">
              <div className="text-center">
                <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-medium text-destructive mb-2">
                  Analytics Loading Failed
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {error}
                </p>
                <Button onClick={onRefresh} variant="outline">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </AnalyticsErrorBoundary>
    );
  }

  // Show empty state if no data
  if (!data) {
    return (
      <AnalyticsErrorBoundary>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={onRefresh}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>
          </div>
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-muted-foreground mb-2">
                  No Analytics Data
                </h3>
                <p className="text-sm text-muted-foreground">
                  No analytics data available for the selected time range.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </AnalyticsErrorBoundary>
    );
  }

  if (!isClient) {
    return (
      <div className="space-y-6">
        <div className="h-64 bg-gray-100 animate-pulse rounded-lg"></div>
        <div className="h-64 bg-gray-100 animate-pulse rounded-lg"></div>
        <div className="h-64 bg-gray-100 animate-pulse rounded-lg"></div>
      </div>
    );
  }

  const queriesChartData = {
    labels: data.queries_over_time.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Queries',
        data: data.queries_over_time.map(item => item.count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const validationsChartData = {
    labels: data.validations_over_time.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Validations',
        data: data.validations_over_time.map(item => item.count),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const topicsChartData = {
    labels: data.top_topics.map(item => item.topic),
    datasets: [
      {
        data: data.top_topics.map(item => item.count),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  };

  return (
    <AnalyticsErrorBoundary>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
            <p className="text-muted-foreground">
              Platform performance and usage insights
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {onTimeRangeChange && (
              <div className="flex items-center space-x-1">
                {(["7d", "30d", "90d"] as const).map((range) => (
                  <Button
                    key={range}
                    variant={timeRange === range ? "default" : "outline"}
                    size="sm"
                    onClick={() => onTimeRangeChange(range)}
                  >
                    {range}
                  </Button>
                ))}
              </div>
            )}
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.total_queries.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="inline h-3 w-3 mr-1" />
                +12% from last period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expert Validations</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.expert_validations.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <Users className="inline h-3 w-3 mr-1" />
                Expert-reviewed responses
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatResponseTime(data.average_response_time)}</div>
              <p className="text-xs text-muted-foreground">
                <Activity className="inline h-3 w-3 mr-1" />
                System performance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatTime(data.time_saved_per_query)}</div>
              <p className="text-xs text-muted-foreground">
                <Target className="inline h-3 w-3 mr-1" />
                Per query average
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Query Volume Over Time</CardTitle>
              <CardDescription>
                Number of queries processed over the selected period
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Line 
                data={queriesChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
                height={300}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Expert Validations</CardTitle>
              <CardDescription>
                Expert validation activity over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Line 
                data={validationsChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
                height={300}
              />
            </CardContent>
          </Card>
        </div>

        {/* Top Topics */}
        <Card>
          <CardHeader>
            <CardTitle>Top Research Topics</CardTitle>
            <CardDescription>
              Most frequently researched topics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Doughnut 
                data={topicsChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest platform activity and events
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.recent_activity.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {activity.type === "query" && <BarChart3 className="h-4 w-4 text-blue-600" />}
                    {activity.type === "validation" && <CheckCircle className="h-4 w-4 text-green-600" />}
                    {activity.type === "feedback" && <Users className="h-4 w-4 text-purple-600" />}
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
            </div>
          </CardContent>
        </Card>
      </div>
    </AnalyticsErrorBoundary>
  );
}
