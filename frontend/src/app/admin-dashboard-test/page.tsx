export const dynamic = 'force-dynamic';

"use client";

import { useEffect, useState } from 'react';
import { Activity, Server, Database, Cpu, HardDrive, Clock, AlertCircle, CheckCircle } from 'lucide-react';

interface SystemStatus {
  [key: string]: string;
}

interface Metrics {
  [key: string]: any;
}

interface SystemDiagnostics {
  timestamp: string;
  system_health?: {
    [key: string]: string;
  };
  memory_statistics?: {
    [key: string]: any;
  };
  orchestration_metrics?: {
    [key: string]: any;
  };
  expert_network_stats?: {
    [key: string]: any;
  };
  environment?: {
    environment: string;
    python_version: string;
    uptime_seconds: number;
  };
}

export default function AdminDashboardTest() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({});
  const [metrics, setMetrics] = useState<Metrics>({});
  const [diagnostics, setDiagnostics] = useState<SystemDiagnostics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch system diagnostics
        const diagnosticsRes = await fetch('/api/system/diagnostics');
        if (diagnosticsRes.ok) {
          const diagnosticsData = await diagnosticsRes.json();
          setDiagnostics(diagnosticsData);
          
          // Extract service status from system health
          if (diagnosticsData.system_health) {
            setSystemStatus(diagnosticsData.system_health);
          }
        } else {
          console.error('Failed to fetch system diagnostics:', diagnosticsRes.status);
        }

        // Fetch metrics
        const metricsRes = await fetch('/api/metrics');
        if (metricsRes.ok) {
          const metricsData = await metricsRes.json();
          setMetrics(metricsData.metrics || metricsData);
        } else {
          console.error('Failed to fetch metrics:', metricsRes.status);
        }
      } catch (err) {
        console.error('Error fetching admin data:', err);
        setError('Failed to load system data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusIcon = (status: string) => {
    return status === 'online' || status === 'healthy' ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <AlertCircle className="h-5 w-5 text-red-500" />
    );
  };

  const getStatusColor = (status: string) => {
    return status === 'online' || status === 'healthy' 
      ? 'bg-green-50 border-green-200 text-green-800' 
      : 'bg-red-50 border-red-200 text-red-800';
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">System Diagnostics (Test Mode)</h1>
          {diagnostics?.timestamp && (
            <div className="text-sm text-gray-500">
              Last updated: {new Date(diagnostics.timestamp).toLocaleString()}
            </div>
          )}
        </div>

        {/* Service Status */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Server className="h-5 w-5 mr-2" />
              Service Status
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(systemStatus).map(([service, status]) => (
                <div
                  key={service}
                  className={`p-4 border rounded-lg flex items-center justify-between ${getStatusColor(status)}`}
                >
                  <div>
                    <div className="font-medium capitalize">
                      {service.replace(/_/g, ' ')}
                    </div>
                    <div className="text-sm opacity-75">
                      {status}
                    </div>
                  </div>
                  {getStatusIcon(status)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Metrics */}
        {metrics && Object.keys(metrics).length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                System Metrics
              </h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(metrics).map(([metric, value]) => (
                  <div key={metric} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-600 capitalize">
                      {metric.replace(/_/g, ' ')}
                    </div>
                    <div className="text-2xl font-bold text-gray-900">
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Environment Information */}
        {diagnostics?.environment && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Cpu className="h-5 w-5 mr-2" />
                Environment Information
              </h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Environment</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {diagnostics.environment.environment}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Python Version</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {diagnostics.environment.python_version}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Uptime</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatUptime(diagnostics.environment.uptime_seconds)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Memory Statistics */}
        {diagnostics?.memory_statistics && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <HardDrive className="h-5 w-5 mr-2" />
                Memory Statistics
              </h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(diagnostics.memory_statistics).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}
                    </div>
                    <div className="text-lg font-semibold text-gray-900">
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 