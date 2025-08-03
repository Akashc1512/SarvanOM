export const dynamic = 'force-dynamic';

"use client";

import { useEffect, useState } from 'react';
import { AnalyticsCard } from '@/ui/analytics-card';

interface AnalyticsData {
  totalQueries: number;
  avgLatency: number;
  llmCosts: number;
  topTopics: string[];
  agentMetrics: Array<{
    name: string;
    latency: number;
    successRate: number;
  }>;
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch('/api/analytics');
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const data = await response.json();
        setAnalytics(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive insights into system performance and usage patterns</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <AnalyticsCard 
          title="Total Queries Processed" 
          value={analytics?.totalQueries?.toLocaleString() || '0'} 
          icon="📊"
        />
        <AnalyticsCard 
          title="Avg Response Latency" 
          value={`${analytics?.avgLatency || 0} ms`} 
          icon="⏱️"
        />
        <AnalyticsCard 
          title="LLM API Costs (This Month)" 
          value={`$${analytics?.llmCosts?.toFixed(2) || '0.00'}`} 
          icon="💰"
        />
        <AnalyticsCard 
          title="Active Users" 
          value={analytics?.totalQueries ? Math.floor(analytics.totalQueries / 10) : '0'} 
          icon="👥"
        />
      </div>

      {analytics?.topTopics && analytics.topTopics.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Queried Topics</h2>
          <div className="flex flex-wrap gap-2">
            {analytics.topTopics.map((topic, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {analytics?.agentMetrics && analytics.agentMetrics.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Agent Performance</h2>
          <div className="space-y-4">
            {analytics.agentMetrics.map((agent) => (
              <div key={agent.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-gray-900">{agent.name}</span>
                </div>
                <div className="flex items-center space-x-6">
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Latency:</span> {agent.latency} ms
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Success Rate:</span> {agent.successRate}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 