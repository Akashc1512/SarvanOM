"use client";

export const dynamic = 'force-dynamic';

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/services/api";
import type {
  SystemMetrics,
  IntegrationStatus,
  ApiInfo,
  AnalyticsData,
} from "@/types/api";
import AgentToolkit from "@/ui/AgentToolkit";
import { motion } from "framer-motion";
import { 
  Activity, 
  Server, 
  BarChart3, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Users,
  Zap,
  Shield,
  Database
} from "lucide-react";

interface ErrorResponse {
  error: string;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | ErrorResponse | null>(
    null,
  );
  const [integrations, setIntegrations] = useState<
    IntegrationStatus | ErrorResponse | null
  >(null);
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null);
  const [analytics, setAnalytics] = useState<
    AnalyticsData | ErrorResponse | null
  >(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Load all dashboard data
  useEffect(() => {
    loadDashboardData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Load all data in parallel
      const [metricsData, integrationsData, apiInfoData, analyticsData] =
        await Promise.all([
          api.getMetrics().catch((err) => ({ error: err.message })),
          api.getIntegrationStatus().catch((err) => ({ error: err.message })),
          api.getApiInfo().catch((err) => ({ error: err.message })),
          api.getAnalytics().catch((err) => ({ error: err.message })),
        ]);

      setMetrics(metricsData as SystemMetrics | ErrorResponse);
      setIntegrations(integrationsData as IntegrationStatus | ErrorResponse);
      setApiInfo(apiInfoData as ApiInfo);
      setAnalytics(analyticsData as AnalyticsData | ErrorResponse);
      setLastRefresh(new Date());
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard data",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-400 bg-green-500/10 border-green-500/20";
      case "unhealthy":
        return "text-red-400 bg-red-500/10 border-red-500/20";
      case "not_configured":
        return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
      default:
        return "text-gray-400 bg-gray-500/10 border-gray-500/20";
    }
  };

  return (
    <div className="min-h-screen cosmic-bg-primary">
      <div className="cosmic-container cosmic-section">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Navigation - Industry Standard */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-wrap gap-4"
          >
            <Link
              href="/"
              className="cosmic-btn-secondary"
            >
              New Query
            </Link>
            <Link
              href="/queries"
              className="cosmic-btn-secondary"
            >
              Manage Queries
            </Link>
            <Link
              href="/dashboard"
              className="cosmic-btn-primary"
            >
              Dashboard
            </Link>
          </motion.div>

          {/* Header - Industry Standard */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6"
          >
            <div className="space-y-2">
              <h1 className="text-4xl sm:text-5xl font-bold cosmic-text-primary">
                System Dashboard
              </h1>
              <p className="text-lg cosmic-text-secondary max-w-2xl">
                Monitor system health, performance, and integrations in real-time
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={loadDashboardData}
                disabled={isLoading}
                className="cosmic-btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? "Refreshing..." : "Refresh"}
              </button>
              <div className="text-right">
                <p className="text-sm cosmic-text-tertiary">
                  Last updated: {lastRefresh.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Error State */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="cosmic-card border-cosmic-error bg-cosmic-error/5 p-6"
            >
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-cosmic-error" />
                <div>
                  <h3 className="font-semibold text-cosmic-error">Error Loading Dashboard</h3>
                  <p className="text-cosmic-error/80 text-sm mt-1">{error}</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Quick Stats Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {[
              {
                title: "Total Requests",
                value: metrics && !("error" in metrics) ? (metrics.sarvanom_requests_total || 0).toLocaleString() : "0",
                icon: Activity,
                color: "text-blue-400",
                bgColor: "bg-blue-500/10",
                trend: "+15.2%",
                trendUp: true
              },
              {
                title: "Active Users",
                value: metrics && !("error" in metrics) ? (metrics.sarvanom_active_users || 0).toLocaleString() : "0",
                icon: Users,
                color: "text-green-400",
                bgColor: "bg-green-500/10",
                trend: "+8.7%",
                trendUp: true
              },
              {
                title: "Avg Response Time",
                value: metrics && !("error" in metrics) ? `${((metrics.sarvanom_average_response_time_seconds || 0) * 1000).toFixed(0)}ms` : "0ms",
                icon: Clock,
                color: "text-yellow-400",
                bgColor: "bg-yellow-500/10",
                trend: "-12.3%",
                trendUp: false
              },
              {
                title: "Cache Hit Rate",
                value: metrics && !("error" in metrics) ? `${((metrics.sarvanom_cache_hits_total || 0) / ((metrics.sarvanom_cache_hits_total || 0) + (metrics.sarvanom_cache_misses_total || 0)) * 100).toFixed(1)}%` : "0%",
                icon: Zap,
                color: "text-purple-400",
                bgColor: "bg-purple-500/10",
                trend: "+5.8%",
                trendUp: true
              }
            ].map((stat, index) => (
              <div key={stat.title} className="cosmic-tile-metric cosmic-hover-lift">
                <div className="flex items-center justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium cosmic-text-tertiary">{stat.title}</p>
                    <p className="text-2xl font-bold cosmic-text-primary">{stat.value}</p>
                    <div className="flex items-center gap-1">
                      {stat.trendUp ? (
                        <ArrowUpRight className="w-4 h-4 text-cosmic-success" />
                      ) : (
                        <ArrowDownRight className="w-4 h-4 text-cosmic-error" />
                      )}
                      <span className={`text-sm font-medium ${stat.trendUp ? 'text-cosmic-success' : 'text-cosmic-error'}`}>
                        {stat.trend}
                      </span>
                    </div>
                  </div>
                  <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center cosmic-glow-soft`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Dashboard Grid - Industry Standard */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-8"
          >
            {/* API Information */}
            <div className="cosmic-analytics-card">
              <div className="flex items-center gap-3 mb-6">
                <Server className="w-6 h-6 text-cosmic-primary-500" />
                <h2 className="text-2xl font-semibold cosmic-text-primary">API Information</h2>
              </div>
              {apiInfo ? (
                <div className="space-y-4">
                  {[
                    { label: "Name", value: apiInfo.name },
                    { label: "Version", value: apiInfo.version },
                    { label: "Environment", value: apiInfo.environment },
                    { label: "Uptime", value: formatUptime(apiInfo.uptime) }
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center py-2 border-b border-cosmic-border-primary">
                      <span className="cosmic-text-tertiary">{item.label}:</span>
                      <span className="font-medium cosmic-text-primary">{item.value}</span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center py-2">
                    <span className="cosmic-text-tertiary">Status:</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(apiInfo.status)}`}>
                      {apiInfo.status}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="cosmic-text-tertiary">Loading API information...</div>
              )}
            </div>

            {/* System Metrics */}
            <div className="cosmic-analytics-card">
              <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-6 h-6 text-cosmic-primary-500" />
                <h2 className="text-2xl font-semibold cosmic-text-primary">System Metrics</h2>
              </div>
              {metrics && !("error" in metrics) ? (
                <div className="space-y-4">
                  {[
                    { label: "Total Requests", value: (metrics.sarvanom_requests_total || 0).toLocaleString(), color: "cosmic-text-primary" },
                    { label: "Errors", value: (metrics.sarvanom_errors_total || 0).toLocaleString(), color: "text-cosmic-error" },
                    { label: "Cache Hits", value: (metrics.sarvanom_cache_hits_total || 0).toLocaleString(), color: "text-cosmic-success" },
                    { label: "Cache Misses", value: (metrics.sarvanom_cache_misses_total || 0).toLocaleString(), color: "text-cosmic-warning" },
                    { label: "Avg Response Time", value: `${((metrics.sarvanom_average_response_time_seconds || 0) * 1000).toFixed(0)}ms`, color: "cosmic-text-primary" },
                    { label: "Active Users", value: (metrics.sarvanom_active_users || 0).toLocaleString(), color: "cosmic-text-primary" }
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center py-2 border-b border-cosmic-border-primary">
                      <span className="cosmic-text-tertiary">{item.label}:</span>
                      <span className={`font-medium ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="cosmic-text-tertiary">
                  {"error" in (metrics || {})
                    ? `Error: ${(metrics as ErrorResponse).error}`
                    : "Loading metrics..."}
                </div>
              )}
            </div>

            {/* Analytics */}
            <div className="cosmic-analytics-card">
              <div className="flex items-center gap-3 mb-6">
                <Database className="w-6 h-6 text-cosmic-primary-500" />
                <h2 className="text-2xl font-semibold cosmic-text-primary">Analytics</h2>
              </div>
              {analytics && !("error" in analytics) ? (
                <div className="space-y-4">
                  {[
                    { label: "Total Queries", value: analytics.total_queries.toLocaleString(), color: "cosmic-text-primary" },
                    { label: "Successful", value: analytics.successful_queries.toLocaleString(), color: "text-cosmic-success" },
                    { label: "Failed", value: analytics.failed_queries.toLocaleString(), color: "text-cosmic-error" },
                    { label: "Avg Confidence", value: `${(analytics.average_confidence * 100).toFixed(1)}%`, color: "cosmic-text-primary" },
                    ...(analytics.cache_hit_rate !== undefined ? [{ label: "Cache Hit Rate", value: `${(analytics.cache_hit_rate * 100).toFixed(1)}%`, color: "cosmic-text-primary" }] : [])
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center py-2 border-b border-cosmic-border-primary">
                      <span className="cosmic-text-tertiary">{item.label}:</span>
                      <span className={`font-medium ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="cosmic-text-tertiary">
                  {analytics?.error
                    ? `Error: ${analytics.error}`
                    : "Loading analytics..."}
                </div>
              )}
            </div>

            {/* Integration Status */}
            <div className="cosmic-analytics-card">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="w-6 h-6 text-cosmic-primary-500" />
                <h2 className="text-2xl font-semibold cosmic-text-primary">Integration Status</h2>
              </div>
              {integrations && !('error' in integrations) ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="cosmic-card p-4 border-cosmic-success bg-cosmic-success/5">
                      <div className="text-2xl font-bold text-cosmic-success">
                        {integrations.summary.healthy}
                      </div>
                      <div className="text-sm cosmic-text-tertiary">Healthy</div>
                    </div>
                    <div className="cosmic-card p-4 border-cosmic-error bg-cosmic-error/5">
                      <div className="text-2xl font-bold text-cosmic-error">
                        {integrations.summary.unhealthy}
                      </div>
                      <div className="text-sm cosmic-text-tertiary">Unhealthy</div>
                    </div>
                    <div className="cosmic-card p-4 border-cosmic-warning bg-cosmic-warning/5">
                      <div className="text-2xl font-bold text-cosmic-warning">
                        {integrations.summary.not_configured}
                      </div>
                      <div className="text-sm cosmic-text-tertiary">Not Configured</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(integrations.integrations).map(
                      ([name, info]) => (
                        <div
                          key={name}
                          className="cosmic-card p-3 flex justify-between items-center"
                        >
                          <span className="font-medium cosmic-text-primary capitalize">
                            {name.replace("_", " ")}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(info.status)}`}>
                            {info.status}
                          </span>
                        </div>
                      ),
                    )}
                  </div>
                </div>
              ) : (
                <div className="cosmic-text-tertiary">
                  {integrations && "error" in integrations
                    ? `Error: ${integrations.error}`
                    : "Loading integration status..."}
                </div>
              )}
            </div>
          </motion.div>

          {/* Agent Toolkit */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <AgentToolkit
              availableAgents={[
                {
                  id: 'browser',
                  name: 'Web Search',
                  description: 'Search the web for real-time information',
                  icon: () => <span>🔍</span>,
                  category: 'search' as const,
                  status: 'available' as const,
                  endpoint: '/api/agents/browser'
                },
                {
                  id: 'pdf',
                  name: 'PDF Processor',
                  description: 'Upload and analyze PDF documents',
                  icon: () => <span>📄</span>,
                  category: 'document' as const,
                  status: 'available' as const,
                  endpoint: '/api/agents/pdf'
                },
                {
                  id: 'code',
                  name: 'Code Executor',
                  description: 'Run and execute code snippets',
                  icon: () => <span>💻</span>,
                  category: 'code' as const,
                  status: 'available' as const,
                  endpoint: '/api/agents/code-executor'
                }
              ]}
              onToolSelected={(agentId, result) => {
                console.log(`Dashboard: Agent ${agentId} selected with result:`, result);
              }}
            />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
