"use client";

import { useState, useEffect } from "react";
import { Sparkles, Zap, Activity, Cpu, HardDrive, Wifi, Play, Pause, RotateCcw, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Progress } from "@/ui/ui/progress";
import { TestRunner } from "@/ui/TestRunner";
import { PerformanceMonitor } from "@/ui/PerformanceMonitor";
import { useTestRunner } from "@/ui/TestRunner";
import { usePerformanceMonitor } from "@/ui/PerformanceMonitor";
import { cn } from "@/lib/utils";

export default function TestingDemoPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState({
    total: 40,
    passed: 32,
    failed: 6,
    skipped: 2,
    duration: 15.3
  });

  const { isOpen: isTestRunnerOpen, toggleTestRunner } = useTestRunner();
  const { isOpen: isPerformanceMonitorOpen, togglePerformanceMonitor } = usePerformanceMonitor();

  // Simulate test execution
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        setTestResults(prev => ({
          ...prev,
          passed: prev.passed + Math.floor(Math.random() * 2),
          failed: prev.failed + Math.floor(Math.random() * 1),
          duration: prev.duration + 0.1
        }));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const startTests = () => {
    setIsRunning(true);
    setTestResults({
      total: 40,
      passed: 0,
      failed: 0,
      skipped: 2,
      duration: 0
    });
  };

  const stopTests = () => {
    setIsRunning(false);
  };

  const resetTests = () => {
    setIsRunning(false);
    setTestResults({
      total: 40,
      passed: 32,
      failed: 6,
      skipped: 2,
      duration: 15.3
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "passed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "failed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "running":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "skipped":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "passed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <Zap className="h-4 w-4 text-yellow-500 animate-pulse" />;
      case "skipped":
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
      default:
        return <div className="h-4 w-4 rounded-full bg-gray-300" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      {/* Cosmic Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-blue-500/5 to-cyan-500/5" />
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-20 w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
          <div className="absolute top-40 right-32 w-1 h-1 bg-blue-400 rounded-full animate-pulse delay-100" />
          <div className="absolute bottom-32 left-1/4 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse delay-200" />
          <div className="absolute top-1/2 right-1/4 w-1 h-1 bg-purple-300 rounded-full animate-pulse delay-300" />
        </div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="relative">
              <Sparkles className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
               Testing & Performance Demo
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Experience comprehensive testing and performance monitoring with cosmic styling. 
            Run tests, monitor system performance, and track real-time metrics.
          </p>
        </div>

        {/* Test Results Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Passed Tests</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{testResults.passed}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-red-100 dark:bg-red-900/50 rounded-lg">
                  <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Failed Tests</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{testResults.failed}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Skipped Tests</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{testResults.skipped}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                  <Activity className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Duration</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{testResults.duration.toFixed(1)}s</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Test Controls */}
        <div className="max-w-4xl mx-auto mb-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                Test Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Test Execution</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Total Tests: {testResults.total} | Coverage: {Math.round(((testResults.passed + testResults.failed) / testResults.total) * 100)}%
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={isRunning ? "default" : "secondary"}
                    className={cn(
                      isRunning 
                        ? "bg-yellow-500 text-white" 
                        : "bg-gray-500 text-white"
                    )}
                  >
                    {isRunning ? "Running" : "Idle"}
                  </Badge>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Button
                  variant={isRunning ? "outline" : "default"}
                  onClick={isRunning ? stopTests : startTests}
                  className="flex-1"
                >
                  {isRunning ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop Tests
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start Tests
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={resetTests}
                  className="flex-1"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset Tests
                </Button>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Test Progress</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {Math.round(((testResults.passed + testResults.failed) / testResults.total) * 100)}%
                  </span>
                </div>
                <Progress 
                  value={((testResults.passed + testResults.failed) / testResults.total) * 100} 
                  className="h-2"
                />
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>Duration: {testResults.duration.toFixed(1)}s</span>
                  <span>Passed: {testResults.passed} | Failed: {testResults.failed} | Skipped: {testResults.skipped}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feature Showcase */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Test Runner Features */}
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                  Test Runner Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
                      <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Real-time Testing</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Run unit, integration, and E2E tests with live progress tracking
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Test Categories</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Unit, Integration, E2E, and Visual regression tests
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                      <Activity className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Detailed Results</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        View individual test results with timing and error details
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
                      <Zap className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Performance Metrics</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Track test execution time and performance bottlenecks
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Performance Monitor Features */}
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                  Performance Monitor Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-cyan-100 dark:bg-cyan-900/50 rounded-lg">
                      <Cpu className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">System Resources</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Monitor CPU, memory, and network usage in real-time
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
                      <Wifi className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Network Monitoring</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Track API requests, response times, and error rates
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                      <Zap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Web Vitals</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Core Web Vitals: FCP, LCP, FID, CLS, and TTFB
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                      <HardDrive className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Memory Analysis</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Detailed memory usage and garbage collection metrics
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Instructions */}
        <div className="max-w-4xl mx-auto mt-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                How to Use
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Test Runner</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li>• Click the test runner button (bottom right) to open the panel</li>
                    <li>• Use "Run All Tests" to start test execution</li>
                    <li>• View detailed results and performance metrics</li>
                    <li>• Monitor test progress in real-time</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Performance Monitor</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li>• Click the performance monitor button to view system metrics</li>
                    <li>• Monitor memory usage, CPU performance, and network activity</li>
                    <li>• Track Core Web Vitals and application performance</li>
                    <li>• View recent API requests and response times</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Testing Components */}
      <TestRunner isOpen={isTestRunnerOpen} onToggle={toggleTestRunner} />
      <PerformanceMonitor isOpen={isPerformanceMonitorOpen} onToggle={togglePerformanceMonitor} />
    </div>
  );
}
