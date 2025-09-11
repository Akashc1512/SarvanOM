/**
 * Analytics Page - SarvanOM v2
 * Comprehensive analytics dashboard with usage metrics and performance data.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Search, 
  Clock, 
  Zap,
  Download,
  RefreshCw
} from 'lucide-react';

interface AnalyticsData {
  overview: {
    totalQueries: number;
    avgResponseTime: number;
    successRate: number;
    userSatisfaction: number;
    guidedPromptUsage: number;
  };
  sourceUsage: Array<{ source: string; count: number; percentage: number }>;
  guidedPromptMetrics: {
    acceptRate: number;
    editRate: number;
    skipRate: number;
    avgRefinementTime: number;
  };
}

export default function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data
  const mockData: AnalyticsData = {
    overview: {
      totalQueries: 15420,
      avgResponseTime: 2.3,
      successRate: 94.2,
      userSatisfaction: 4.6,
      guidedPromptUsage: 67.8
    },
    sourceUsage: [
      { source: 'Web Search', count: 5420, percentage: 35.2 },
      { source: 'Vector Search', count: 3890, percentage: 25.2 },
      { source: 'Knowledge Graph', count: 2890, percentage: 18.7 },
      { source: 'News Feeds', count: 1980, percentage: 12.8 },
      { source: 'Market Data', count: 1240, percentage: 8.1 }
    ],
    guidedPromptMetrics: {
      acceptRate: 68.5,
      editRate: 23.2,
      skipRate: 8.3,
      avgRefinementTime: 0.8
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalyticsData(mockData);
      setIsLoading(false);
    };
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
                <p className="text-gray-600">Usage metrics and performance insights</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsLoading(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Queries</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analyticsData.overview.totalQueries.toLocaleString()}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Search className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">+8.5% from last period</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analyticsData.overview.avgResponseTime}s
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-sm text-gray-600">-8.0% from last period</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analyticsData.overview.successRate}%
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">+1.4% from last period</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">User Satisfaction</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analyticsData.overview.userSatisfaction}/5
                </p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Users className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">+4.5% from last period</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.4 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Guided Prompt Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analyticsData.overview.guidedPromptUsage}%
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Zap className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">+21.5% from last period</span>
            </div>
          </motion.div>
        </div>

        {/* Charts and Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Source Usage Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.5 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Usage Distribution</h3>
            <div className="space-y-4">
              {analyticsData.sourceUsage.map((source, index) => (
                <div key={source.source} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-blue-600" />
                    <span className="text-sm font-medium text-gray-700">{source.source}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${source.percentage}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">
                      {source.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Guided Prompt Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.6 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Guided Prompt Performance</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Accept Rate</span>
                <span className="text-sm font-bold text-green-600">
                  {analyticsData.guidedPromptMetrics.acceptRate}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Edit Rate</span>
                <span className="text-sm font-bold text-yellow-600">
                  {analyticsData.guidedPromptMetrics.editRate}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Skip Rate</span>
                <span className="text-sm font-bold text-red-600">
                  {analyticsData.guidedPromptMetrics.skipRate}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Avg Refinement Time</span>
                <span className="text-sm font-bold text-blue-600">
                  {analyticsData.guidedPromptMetrics.avgRefinementTime}s
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Key Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.7 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-lg border-2 text-green-600 bg-green-50 border-green-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium mb-1">Guided Prompt Usage Increasing</h4>
                  <p className="text-sm opacity-90">67.8% of users are now using guided prompt refinement, up 12% from last month</p>
                </div>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  high impact
                </span>
              </div>
            </div>
            
            <div className="p-4 rounded-lg border-2 text-red-600 bg-red-50 border-red-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium mb-1">Response Time Optimization Needed</h4>
                  <p className="text-sm opacity-90">Market data queries are taking 3.2s on average, above the 2.5s target</p>
                </div>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  medium impact
                </span>
              </div>
            </div>
            
            <div className="p-4 rounded-lg border-2 text-green-600 bg-green-50 border-green-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium mb-1">Vector Search Performance Excellent</h4>
                  <p className="text-sm opacity-90">Vector search maintains 98.1% success rate with sub-second response times</p>
                </div>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  high impact
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
