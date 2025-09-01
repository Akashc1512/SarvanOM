"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  ChartBarIcon,
  CpuChipIcon,
  GlobeAltIcon,
  UsersIcon,
  ClockIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  SparklesIcon
} from "@heroicons/react/24/outline";

interface MetricCard {
  title: string;
  value: string | number;
  change: number;
  changeType: "increase" | "decrease";
  icon: React.ComponentType<any>;
  color: string;
  description: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
  }[];
}

export function DataNovaDashboard() {
  const [timeRange, setTimeRange] = useState("7d");
  const [isLoading, setIsLoading] = useState(true);

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const metrics: MetricCard[] = [
    {
      title: "Total Searches",
      value: "12,847",
      change: 23.5,
      changeType: "increase",
      icon: ChartBarIcon,
      color: "from-blue-500 to-cyan-500",
      description: "Search queries processed"
    },
    {
      title: "AI Responses",
      value: "8,923",
      change: 18.2,
      changeType: "increase",
      icon: SparklesIcon,
      color: "from-purple-500 to-pink-500",
      description: "AI-generated answers"
    },
    {
      title: "Active Users",
      value: "2,341",
      change: -5.3,
      changeType: "decrease",
      icon: UsersIcon,
      color: "from-green-500 to-emerald-500",
      description: "Unique users this period"
    },
    {
      title: "Avg Response Time",
      value: "1.2s",
      change: -12.8,
      changeType: "decrease",
      icon: ClockIcon,
      color: "from-orange-500 to-red-500",
      description: "Average AI response time"
    },
    {
      title: "Citations Generated",
      value: "45,678",
      change: 31.7,
      changeType: "increase",
      icon: DocumentTextIcon,
      color: "from-indigo-500 to-purple-500",
      description: "Source citations provided"
    },
    {
      title: "API Calls",
      value: "156,789",
      change: 8.9,
      changeType: "increase",
      icon: CpuChipIcon,
      color: "from-teal-500 to-blue-500",
      description: "Backend API requests"
    }
  ];

  const topQueries = [
    { query: "What are the latest developments in quantum computing?", count: 234, trend: "up" },
    { query: "How does machine learning work?", count: 189, trend: "up" },
    { query: "Explain artificial intelligence", count: 156, trend: "down" },
    { query: "What is blockchain technology?", count: 143, trend: "up" },
    { query: "How to build a web application?", count: 128, trend: "stable" }
  ];

  const userActivity = [
    { time: "00:00", searches: 45, users: 12 },
    { time: "04:00", searches: 23, users: 8 },
    { time: "08:00", searches: 156, users: 45 },
    { time: "12:00", searches: 289, users: 78 },
    { time: "16:00", searches: 234, users: 67 },
    { time: "20:00", searches: 178, users: 52 }
  ];

  const timeRanges = [
    { id: "1d", label: "Last 24h" },
    { id: "7d", label: "Last 7 days" },
    { id: "30d", label: "Last 30 days" },
    { id: "90d", label: "Last 90 days" }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl m-6 p-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-4">
                <ChartBarIcon className="w-4 h-4" />
                DataNova Analytics
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Platform Analytics
              </h1>
              <p className="text-lg text-gray-300">
                Real-time insights into your AI-powered knowledge platform
              </p>
            </motion.div>

            {/* Time Range Selector */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex gap-2"
            >
              {timeRanges.map((range) => (
                <button
                  key={range.id}
                  onClick={() => setTimeRange(range.id)}
                  className={`px-4 py-2 rounded-lg transition-all duration-300 ${
                    timeRange === range.id
                      ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                      : "bg-white/10 text-gray-300 hover:bg-white/20"
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </motion.div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl"
                   style={{ backgroundImage: `linear-gradient(to right, ${metric.color})` }} />
              <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${metric.color}`}>
                    <metric.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className={`flex items-center gap-1 text-sm ${
                    metric.changeType === "increase" ? "text-green-400" : "text-red-400"
                  }`}>
                    {metric.changeType === "increase" ? (
                      <ArrowUpIcon className="w-4 h-4" />
                    ) : (
                      <ArrowDownIcon className="w-4 h-4" />
                    )}
                    {Math.abs(metric.change)}%
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-white mb-1">{metric.value}</h3>
                <p className="text-gray-400 text-sm mb-2">{metric.title}</p>
                <p className="text-gray-500 text-xs">{metric.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts and Data Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Search Activity Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Search Activity</h3>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                Searches
                <div className="w-3 h-3 bg-purple-500 rounded-full ml-4"></div>
                Users
              </div>
            </div>
            <div className="space-y-4">
              {userActivity.map((activity, index) => (
                <div key={activity.time} className="flex items-center gap-4">
                  <div className="w-12 text-gray-400 text-sm">{activity.time}</div>
                  <div className="flex-1 flex items-center gap-2">
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                        style={{ width: `${(activity.searches / 300) * 100}%` }}
                      ></div>
                    </div>
                    <div className="w-16 text-white text-sm text-right">{activity.searches}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Top Queries */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6">Top Search Queries</h3>
            <div className="space-y-4">
              {topQueries.map((query, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex-1">
                    <p className="text-white text-sm mb-1">{query.query}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-xs">{query.count} searches</span>
                      <div className={`flex items-center gap-1 text-xs ${
                        query.trend === "up" ? "text-green-400" : 
                        query.trend === "down" ? "text-red-400" : "text-gray-400"
                      }`}>
                        {query.trend === "up" && <ArrowUpIcon className="w-3 h-3" />}
                        {query.trend === "down" && <ArrowDownIcon className="w-3 h-3" />}
                        {query.trend}
                      </div>
                    </div>
                  </div>
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {index + 1}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
        >
          <h3 className="text-xl font-semibold text-white mb-6">Performance Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <ClockIcon className="w-8 h-8 text-white" />
              </div>
              <h4 className="text-white font-semibold mb-2">Response Time</h4>
              <p className="text-2xl font-bold text-green-400 mb-1">1.2s</p>
              <p className="text-gray-400 text-sm">Average response time</p>
            </div>
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <EyeIcon className="w-8 h-8 text-white" />
              </div>
              <h4 className="text-white font-semibold mb-2">Uptime</h4>
              <p className="text-2xl font-bold text-blue-400 mb-1">99.9%</p>
              <p className="text-gray-400 text-sm">System availability</p>
            </div>
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftRightIcon className="w-8 h-8 text-white" />
              </div>
              <h4 className="text-white font-semibold mb-2">Satisfaction</h4>
              <p className="text-2xl font-bold text-purple-400 mb-1">4.8/5</p>
              <p className="text-gray-400 text-sm">User satisfaction</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
