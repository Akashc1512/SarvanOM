"use client";

import { useState, useEffect, useCallback } from "react";
import { Activity, Cpu, HardDrive, Wifi, Zap, TrendingUp, TrendingDown, Sparkles, Eye, EyeOff } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Progress } from "@/ui/ui/progress";
import { cn } from "@/lib/utils";

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  status: "good" | "warning" | "critical";
  trend: "up" | "down" | "stable";
  timestamp: Date;
}

interface NetworkRequest {
  url: string;
  method: string;
  status: number;
  duration: number;
  timestamp: Date;
}

interface PerformanceData {
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  cpu: {
    usage: number;
    cores: number;
  };
  network: {
    requests: number;
    errors: number;
    avgResponseTime: number;
  };
  webVitals: {
    fcp: number; // First Contentful Paint
    lcp: number; // Largest Contentful Paint
    fid: number; // First Input Delay
    cls: number; // Cumulative Layout Shift
    ttfb: number; // Time to First Byte
  };
  metrics: PerformanceMetric[];
  recentRequests: NetworkRequest[];
}

interface PerformanceMonitorProps {
  className?: string;
  isOpen?: boolean;
  onToggle?: () => void;
}

export function PerformanceMonitor({
  className = "",
  isOpen = false,
  onToggle
}: PerformanceMonitorProps) {
  const [performanceData, setPerformanceData] = useState<PerformanceData>({
    memory: {
      used: 45.2,
      total: 128,
      percentage: 35.3
    },
    cpu: {
      usage: 12.5,
      cores: 8
    },
    network: {
      requests: 24,
      errors: 1,
      avgResponseTime: 245
    },
    webVitals: {
      fcp: 1200,
      lcp: 2800,
      fid: 45,
      cls: 0.08,
      ttfb: 180
    },
    metrics: [
      {
        name: "Memory Usage",
        value: 35.3,
        unit: "%",
        status: "good",
        trend: "stable",
        timestamp: new Date()
      },
      {
        name: "CPU Usage",
        value: 12.5,
        unit: "%",
        status: "good",
        trend: "down",
        timestamp: new Date()
      },
      {
        name: "Network Requests",
        value: 24,
        unit: "req/min",
        status: "good",
        trend: "up",
        timestamp: new Date()
      },
      {
        name: "Error Rate",
        value: 4.2,
        unit: "%",
        status: "warning",
        trend: "up",
        timestamp: new Date()
      }
    ],
    recentRequests: [
      {
        url: "/api/query",
        method: "POST",
        status: 200,
        duration: 245,
        timestamp: new Date()
      },
      {
        url: "/api/collaboration",
        method: "GET",
        status: 200,
        duration: 180,
        timestamp: new Date()
      },
      {
        url: "/api/analytics",
        method: "POST",
        status: 500,
        duration: 1200,
        timestamp: new Date()
      }
    ]
  });

  const [showDetails, setShowDetails] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Simulate real-time performance updates
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      setPerformanceData(prev => ({
        ...prev,
        memory: {
          ...prev.memory,
          used: prev.memory.used + (Math.random() - 0.5) * 2,
          percentage: Math.max(0, Math.min(100, prev.memory.percentage + (Math.random() - 0.5) * 2))
        },
        cpu: {
          ...prev.cpu,
          usage: Math.max(0, Math.min(100, prev.cpu.usage + (Math.random() - 0.5) * 5))
        },
        network: {
          ...prev.network,
          requests: prev.network.requests + Math.floor(Math.random() * 3),
          avgResponseTime: Math.max(50, prev.network.avgResponseTime + (Math.random() - 0.5) * 50)
        },
        metrics: prev.metrics.map(metric => ({
          ...metric,
          value: metric.value + (Math.random() - 0.5) * 2,
          timestamp: new Date()
        }))
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "warning":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "critical":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-3 w-3 text-green-500" />;
      case "down":
        return <TrendingDown className="h-3 w-3 text-red-500" />;
      default:
        return <div className="h-3 w-3" />;
    }
  };

  const getWebVitalStatus = (value: number, threshold: number) => {
    if (value <= threshold) return "good";
    if (value <= threshold * 1.5) return "warning";
    return "critical";
  };

  const totalRequests = performanceData.network.requests;
  const errorRate = (performanceData.network.errors / totalRequests) * 100;
  const avgResponseTime = performanceData.network.avgResponseTime;

  return (
    <div className={cn("relative", className)}>
      {/* Performance Monitor Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        className={cn(
          "fixed bottom-44 right-4 z-50 rounded-full w-12 h-12 p-0",
          "bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:bg-white dark:hover:bg-slate-800",
          "transition-all duration-300 hover:scale-110",
          "shadow-lg hover:shadow-xl"
        )}
      >
        <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        {errorRate > 5 && (
          <Badge 
            variant="secondary" 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-red-500 text-white"
          >
            !
          </Badge>
        )}
      </Button>

      {/* Performance Monitor Panel */}
      {isOpen && (
        <div className="fixed bottom-56 right-4 z-40 w-96 max-h-[80vh] overflow-hidden">
          <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardHeader className="pb-3 border-b border-gray-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Performance Monitor
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {Math.round(performanceData.memory.percentage)}% RAM
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDetails(!showDetails)}
                  >
                    {showDetails ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-0">
              <div className="max-h-96 overflow-y-auto">
                {/* System Overview */}
                <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <HardDrive className="h-4 w-4 text-blue-500" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Memory</span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600 dark:text-gray-400">Usage</span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {performanceData.memory.used.toFixed(1)}GB / {performanceData.memory.total}GB
                          </span>
                        </div>
                        <Progress 
                          value={performanceData.memory.percentage} 
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <Cpu className="h-4 w-4 text-green-500" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">CPU</span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600 dark:text-gray-400">Usage</span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {performanceData.cpu.usage.toFixed(1)}%
                          </span>
                        </div>
                        <Progress 
                          value={performanceData.cpu.usage} 
                          className="h-2"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Network Overview */}
                <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                  <div className="flex items-center space-x-2 mb-3">
                    <Wifi className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Network</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {totalRequests}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Requests</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {errorRate.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Error Rate</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {avgResponseTime.toFixed(0)}ms
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Avg Response</div>
                    </div>
                  </div>
                </div>

                {/* Web Vitals */}
                <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                  <div className="flex items-center space-x-2 mb-3">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Core Web Vitals</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { name: "FCP", value: performanceData.webVitals.fcp, threshold: 1800, unit: "ms" },
                      { name: "LCP", value: performanceData.webVitals.lcp, threshold: 2500, unit: "ms" },
                      { name: "FID", value: performanceData.webVitals.fid, threshold: 100, unit: "ms" },
                      { name: "CLS", value: performanceData.webVitals.cls, threshold: 0.1, unit: "" },
                      { name: "TTFB", value: performanceData.webVitals.ttfb, threshold: 800, unit: "ms" }
                    ].map((vital) => (
                      <div key={vital.name} className="flex items-center justify-between">
                        <span className="text-xs text-gray-600 dark:text-gray-400">{vital.name}</span>
                        <div className="flex items-center space-x-2">
                          <Badge 
                            variant="outline" 
                            className={cn("text-xs", getStatusColor(getWebVitalStatus(vital.value, vital.threshold)))}
                          >
                            {vital.value.toFixed(vital.name === "CLS" ? 3 : 0)}{vital.unit}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Detailed Metrics */}
                {showDetails && (
                  <div className="p-4 space-y-3">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Real-time Metrics</h4>
                    <div className="space-y-2">
                      {performanceData.metrics.map((metric) => (
                        <div
                          key={metric.name}
                          className="flex items-center justify-between p-2 rounded bg-gray-50 dark:bg-slate-700/50"
                        >
                          <div className="flex items-center space-x-2">
                            {getTrendIcon(metric.trend)}
                            <span className="text-xs text-gray-700 dark:text-gray-300">
                              {metric.name}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge 
                              variant="outline" 
                              className={cn("text-xs", getStatusColor(metric.status))}
                            >
                              {metric.value.toFixed(1)}{metric.unit}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Recent Requests */}
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Requests</h4>
                      <div className="space-y-1">
                        {performanceData.recentRequests.map((request, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between text-xs p-2 rounded bg-gray-50 dark:bg-slate-700/50"
                          >
                            <div className="flex items-center space-x-2">
                              <div className={cn(
                                "w-2 h-2 rounded-full",
                                request.status >= 200 && request.status < 300 ? "bg-green-500" :
                                request.status >= 400 && request.status < 500 ? "bg-yellow-500" : "bg-red-500"
                              )} />
                              <span className="text-gray-700 dark:text-gray-300 font-mono">
                                {request.method} {request.url.split('/').pop()}
                              </span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge 
                                variant="outline" 
                                className={cn("text-xs", 
                                  request.status >= 200 && request.status < 300 ? "bg-green-100 text-green-800" :
                                  request.status >= 400 && request.status < 500 ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"
                                )}
                              >
                                {request.status}
                              </Badge>
                              <span className="text-gray-500 dark:text-gray-400">
                                {request.duration}ms
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export function usePerformanceMonitor() {
  const [isOpen, setIsOpen] = useState(false);

  const togglePerformanceMonitor = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    togglePerformanceMonitor,
  };
}
