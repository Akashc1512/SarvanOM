/**
 * Active Data Sources Component - SarvanOM v2
 * 
 * Displays active data sources and fallback status in the Settings page.
 * Implements PR-5 requirements for Settings help panel.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Database, 
  Globe, 
  Newspaper, 
  TrendingUp, 
  Search, 
  Brain,
  Key,
  KeyOff,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProviderStatusBadge } from '@/components/ui/FallbackBadge';

export interface ProviderStatus {
  name: string;
  configured: boolean;
  available: boolean;
  keyless_fallback_enabled: boolean;
  last_check?: string;
  error?: string;
}

export interface DataSourceStatus {
  lane: string;
  providers: ProviderStatus[];
  fallback_enabled: boolean;
  last_updated: string;
}

interface ActiveDataSourcesProps {
  className?: string;
}

export function ActiveDataSources({ className }: ActiveDataSourcesProps) {
  const [dataSources, setDataSources] = useState<DataSourceStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Mock data - in real implementation, this would come from the backend
  const mockDataSources: DataSourceStatus[] = [
    {
      lane: 'web_search',
      fallback_enabled: true,
      last_updated: new Date().toISOString(),
      providers: [
        { name: 'Brave Search', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'SerpAPI', configured: false, available: false, keyless_fallback_enabled: true },
        { name: 'DuckDuckGo IA', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'Wikipedia', configured: true, available: true, keyless_fallback_enabled: true }
      ]
    },
    {
      lane: 'news',
      fallback_enabled: true,
      last_updated: new Date().toISOString(),
      providers: [
        { name: 'Guardian', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'NewsAPI', configured: false, available: false, keyless_fallback_enabled: true },
        { name: 'GDELT', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'HN Algolia', configured: true, available: true, keyless_fallback_enabled: true }
      ]
    },
    {
      lane: 'markets',
      fallback_enabled: true,
      last_updated: new Date().toISOString(),
      providers: [
        { name: 'Alpha Vantage', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'Finnhub', configured: false, available: false, keyless_fallback_enabled: true },
        { name: 'FMP', configured: false, available: false, keyless_fallback_enabled: true },
        { name: 'Stooq', configured: true, available: true, keyless_fallback_enabled: true }
      ]
    },
    {
      lane: 'vector',
      fallback_enabled: true,
      last_updated: new Date().toISOString(),
      providers: [
        { name: 'Qdrant', configured: true, available: true, keyless_fallback_enabled: true },
        { name: 'Meilisearch', configured: true, available: true, keyless_fallback_enabled: true }
      ]
    },
    {
      lane: 'kg',
      fallback_enabled: true,
      last_updated: new Date().toISOString(),
      providers: [
        { name: 'ArangoDB', configured: true, available: true, keyless_fallback_enabled: true }
      ]
    }
  ];

  useEffect(() => {
    // Simulate API call to fetch data sources
    const fetchDataSources = async () => {
      setIsLoading(true);
      try {
        // In real implementation, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setDataSources(mockDataSources);
      } catch (error) {
        console.error('Failed to fetch data sources:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDataSources();
  }, []);

  const handleRefresh = async () => {
    setIsLoading(true);
    setLastRefresh(new Date());
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const getLaneIcon = (lane: string) => {
    switch (lane) {
      case 'web_search': return Globe;
      case 'news': return Newspaper;
      case 'markets': return TrendingUp;
      case 'vector': return Search;
      case 'kg': return Brain;
      default: return Database;
    }
  };

  const getLaneDisplayName = (lane: string) => {
    return lane.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getOverallStatus = (providers: ProviderStatus[]) => {
    const configured = providers.filter(p => p.configured && p.available);
    const total = providers.length;
    
    if (configured.length === total) {
      return { status: 'excellent', label: 'All Active', color: 'text-green-600' };
    } else if (configured.length > 0) {
      return { status: 'good', label: 'Partially Active', color: 'text-yellow-600' };
    } else {
      return { status: 'poor', label: 'Keyless Only', color: 'text-orange-600' };
    }
  };

  if (isLoading) {
    return (
      <div className={cn('bg-white rounded-lg shadow-sm border border-gray-200 p-6', className)}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Active Data Sources</h3>
          <div className="animate-spin">
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-lg shadow-sm border border-gray-200 p-6', className)}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Active Data Sources</h3>
          <p className="text-sm text-gray-600">
            Current status of data providers and fallback options
          </p>
        </div>
        <motion.button
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          Refresh
        </motion.button>
      </div>

      {/* Keyless Fallbacks Status */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <KeyOff className="w-4 h-4 text-blue-600" />
          <span className="font-medium text-blue-900">Keyless Fallbacks</span>
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            ON
          </span>
        </div>
        <p className="text-sm text-blue-800">
          When API keys are not configured, the system automatically uses free, keyless providers 
          to ensure continuous service availability.
        </p>
      </div>

      {/* Data Sources */}
      <div className="space-y-4">
        {dataSources.map((dataSource) => {
          const LaneIcon = getLaneIcon(dataSource.lane);
          const overallStatus = getOverallStatus(dataSource.providers);
          
          return (
            <motion.div
              key={dataSource.lane}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="border border-gray-200 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <LaneIcon className="w-4 h-4 text-gray-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {getLaneDisplayName(dataSource.lane)}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {dataSource.providers.length} providers
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn('text-sm font-medium', overallStatus.color)}>
                    {overallStatus.label}
                  </span>
                  {overallStatus.status === 'excellent' && (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  )}
                  {overallStatus.status === 'good' && (
                    <Clock className="w-4 h-4 text-yellow-600" />
                  )}
                  {overallStatus.status === 'poor' && (
                    <AlertTriangle className="w-4 h-4 text-orange-600" />
                  )}
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {dataSource.providers.map((provider) => (
                  <ProviderStatusBadge
                    key={provider.name}
                    provider={provider.name}
                    available={provider.available}
                    configured={provider.configured}
                  />
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Last Updated */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Last updated: {lastRefresh.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
