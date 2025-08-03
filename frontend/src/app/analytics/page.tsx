"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Progress } from "@/ui/ui/progress";
import { Separator } from "@/ui/ui/separator";
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Users, 
  Zap, 
  Shield, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Calendar,
  Activity,
  Target,
  Award,
  Timer,
  Brain,
  Network,
  BookOpen,
  Star
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface AnalyticsData {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_confidence: number;
  cache_hit_rate: number;
  average_response_time: number;
  total_requests: number;
  total_errors: number;
  popular_queries: Record<string, number>;
  validation_metrics: {
    total_validations: number;
    supported_claims: number;
    contradicted_claims: number;
    unclear_claims: number;
    average_validation_confidence: number;
  };
  time_saved_metrics: {
    total_time_saved_hours: number;
    average_time_per_query_minutes: number;
    efficiency_gain_percentage: number;
  };
  system_health: {
    cpu_usage: number;
    memory_usage: number;
    active_connections: number;
    uptime_hours: number;
  };
  agent_performance: Array<{
    name: string;
    success_rate: number;
    average_latency: number;
    total_calls: number;
  }>;
  timestamp: string;
}

export default function AnalyticsPage() {
  const { toast } = useToast();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/analytics');
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      
      const data = await response.json();
      setAnalytics(data);
      setLastRefresh(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics';
      setError(errorMessage);
      toast({
        title: "Analytics Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const getStatusColor = (value: number, threshold: number = 0.8) => {
    if (value >= threshold) return "text-green-600";
    if (value >= threshold * 0.7) return "text-yellow-600";
    return "text-red-600";
  };

  const getStatusBadgeColor = (value: number, threshold: number = 0.8) => {
    if (value >= threshold) return "bg-green-100 text-green-800";
    if (value >= threshold * 0.7) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
          <Button onClick={fetchAnalytics} className="mt-2">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="text-center py-8">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No analytics data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Comprehensive insights into system performance and usage</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={fetchAnalytics} disabled={isLoading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <span className="text-sm text-gray-500">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Queries */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Queries</p>
                <p className="text-3xl font-bold text-gray-900">
                  {analytics.total_queries.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {analytics.successful_queries} successful
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        {/* Success Rate */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-3xl font-bold text-gray-900">
                  {analytics.total_queries > 0 
                    ? Math.round((analytics.successful_queries / analytics.total_queries) * 100)
                    : 0}%
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {analytics.failed_queries} failed
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        {/* Average Response Time */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-3xl font-bold text-gray-900">
                  {analytics.average_response_time.toFixed(2)}s
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Cache hit: {(analytics.cache_hit_rate * 100).toFixed(1)}%
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        {/* Time Saved */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Time Saved</p>
                <p className="text-3xl font-bold text-gray-900">
                  {analytics.time_saved_metrics.total_time_saved_hours.toFixed(1)}h
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {analytics.time_saved_metrics.efficiency_gain_percentage.toFixed(1)}% efficiency gain
                </p>
              </div>
              <Timer className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Validation Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Expert Validation Metrics
            </CardTitle>
            <CardDescription>
              Fact-checking and validation performance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Validations</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.validation_metrics.total_validations}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Confidence</p>
                <p className={`text-2xl font-bold ${getStatusColor(analytics.validation_metrics.average_validation_confidence)}`}>
                  {(analytics.validation_metrics.average_validation_confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Supported Claims</span>
                <Badge className="bg-green-100 text-green-800">
                  {analytics.validation_metrics.supported_claims}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Contradicted Claims</span>
                <Badge className="bg-red-100 text-red-800">
                  {analytics.validation_metrics.contradicted_claims}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Unclear Claims</span>
                <Badge className="bg-yellow-100 text-yellow-800">
                  {analytics.validation_metrics.unclear_claims}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Health
            </CardTitle>
            <CardDescription>
              Current system performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>CPU Usage</span>
                  <span>{analytics.system_health.cpu_usage.toFixed(1)}%</span>
                </div>
                <Progress value={analytics.system_health.cpu_usage} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Memory Usage</span>
                  <span>{analytics.system_health.memory_usage.toFixed(1)}%</span>
                </div>
                <Progress value={analytics.system_health.memory_usage} className="h-2" />
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <p className="text-sm text-gray-600">Active Connections</p>
                  <p className="text-lg font-semibold">{analytics.system_health.active_connections}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Uptime</p>
                  <p className="text-lg font-semibold">{analytics.system_health.uptime_hours.toFixed(1)}h</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Agent Performance
          </CardTitle>
          <CardDescription>
            Performance metrics for AI agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analytics.agent_performance.map((agent, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium">{agent.name}</h4>
                  <Badge className={getStatusBadgeColor(agent.success_rate / 100)}>
                    {(agent.success_rate).toFixed(1)}%
                  </Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Rate</span>
                    <span className="font-medium">{agent.success_rate.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Latency</span>
                    <span className="font-medium">{agent.average_latency}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Calls</span>
                    <span className="font-medium">{agent.total_calls}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Popular Queries */}
      {analytics.popular_queries && Object.keys(analytics.popular_queries).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Popular Query Categories
            </CardTitle>
            <CardDescription>
              Most frequently asked question types
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(analytics.popular_queries)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
                .map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {category.replace("_", " ")}
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ 
                            width: `${(count / Math.max(...Object.values(analytics.popular_queries))) * 100}%` 
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-500 w-12 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timestamp */}
      <div className="text-center text-sm text-gray-500">
        Data last updated: {new Date(analytics.timestamp).toLocaleString()}
      </div>
    </div>
  );
} 