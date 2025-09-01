"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
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
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";

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

  // Mock data for demonstration
  const mockData: AnalyticsData = {
    total_queries: 1247,
    expert_validations: 89,
    average_response_time: 2.3,
    time_saved_per_query: 15.7,
    top_topics: [
      { topic: "AI & Machine Learning", count: 234 },
      { topic: "Data Science", count: 189 },
      { topic: "Web Development", count: 156 },
      { topic: "Cybersecurity", count: 98 }
    ],
    queries_over_time: [
      { date: "2024-01-01", count: 45 },
      { date: "2024-01-02", count: 52 },
      { date: "2024-01-03", count: 48 }
    ],
    validations_over_time: [
      { date: "2024-01-01", count: 12 },
      { date: "2024-01-02", count: 15 },
      { date: "2024-01-03", count: 8 }
    ],
    recent_activity: [
      {
        id: "1",
        type: "query",
        description: "Advanced search query processed",
        timestamp: "2024-01-03T10:30:00Z"
      },
      {
        id: "2",
        type: "validation",
        description: "Expert validation completed",
        timestamp: "2024-01-03T09:15:00Z"
      }
    ]
  };

  const data = analyticsData || mockData;

  return (
    <div className="min-h-screen bg-cosmos-bg">
      <div className="container mx-auto px-6 sm:px-8 lg:px-12 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header Section */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="space-y-2">
                <h1 className="text-4xl font-bold text-cosmos-fg">
                  Analytics Dashboard
                </h1>
                <p className="text-lg text-cosmos-fg/70">
                  Comprehensive insights into platform performance and user engagement
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex bg-cosmos-card/50 rounded-lg p-1">
                  {(["7d", "30d", "90d"] as const).map((range) => (
                    <button
                      key={range}
                      onClick={() => handleTimeRangeChange(range)}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                        timeRange === range
                          ? "bg-cosmos-accent text-cosmos-bg"
                          : "text-cosmos-fg/70 hover:text-cosmos-fg hover:bg-cosmos-card/30"
                      }`}
                    >
                      {range === "7d" ? "7 Days" : range === "30d" ? "30 Days" : "90 Days"}
                    </button>
                  ))}
                </div>
                
                <button
                  onClick={handleRefresh}
                  disabled={isLoading}
                  className="p-2 rounded-lg bg-cosmos-card/50 text-cosmos-fg hover:bg-cosmos-card/70 transition-all disabled:opacity-50"
                >
                  <RefreshCw className={`w-5 h-5 ${isLoading ? "animate-spin" : ""}`} />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Error State */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-red-500/10 border border-red-500/20 rounded-xl p-6"
            >
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-400" />
                <div>
                  <h3 className="font-semibold text-red-400">Error Loading Analytics</h3>
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Quick Stats Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-cosmos-fg/70">Total Queries</p>
                  <p className="text-3xl font-bold text-cosmos-fg">{data.total_queries.toLocaleString()}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </div>

            <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-cosmos-fg/70">Expert Validations</p>
                  <p className="text-3xl font-bold text-cosmos-fg">{data.expert_validations}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </div>

            <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-cosmos-fg/70">Avg Response Time</p>
                  <p className="text-3xl font-bold text-cosmos-fg">{data.average_response_time}s</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
                  <Clock className="w-6 h-6 text-purple-400" />
                </div>
              </div>
            </div>

            <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-cosmos-fg/70">Time Saved</p>
                  <p className="text-3xl font-bold text-cosmos-fg">{data.time_saved_per_query}m</p>
                </div>
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-orange-400" />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Top Topics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-cosmos-fg mb-6">Top Topics</h3>
            <div className="space-y-4">
              {data.top_topics.map((topic, index) => (
                <div key={topic.topic} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-cosmos-fg/70">#{index + 1}</span>
                    <span className="text-cosmos-fg">{topic.topic}</span>
                  </div>
                  <span className="text-cosmos-accent font-semibold">{topic.count}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-cosmos-fg mb-6">Recent Activity</h3>
            <div className="space-y-4">
              {data.recent_activity.map((activity) => (
                <div key={activity.id} className="flex items-center gap-3 p-3 rounded-lg bg-cosmos-bg/20">
                  <div className="w-2 h-2 rounded-full bg-cosmos-accent"></div>
                  <div className="flex-1">
                    <p className="text-cosmos-fg text-sm">{activity.description}</p>
                    <p className="text-cosmos-fg/50 text-xs">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
        </div>
      </div>
  );
} 