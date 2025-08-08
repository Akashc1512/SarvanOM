"use client";

import { useState, useEffect, useCallback } from "react";
import { Play, Pause, RotateCcw, CheckCircle, XCircle, AlertTriangle, Zap, Sparkles, Eye, EyeOff } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Progress } from "@/ui/ui/progress";
import { cn } from "@/lib/utils";

interface TestResult {
  id: string;
  name: string;
  status: "pending" | "running" | "passed" | "failed" | "skipped";
  duration: number;
  error?: string;
  category: "unit" | "integration" | "e2e" | "visual";
  timestamp: Date;
}

interface TestSuite {
  id: string;
  name: string;
  description: string;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  duration: number;
  status: "idle" | "running" | "completed" | "failed";
  results: TestResult[];
}

interface TestRunnerProps {
  className?: string;
  isOpen?: boolean;
  onToggle?: () => void;
}

export function TestRunner({
  className = "",
  isOpen = false,
  onToggle
}: TestRunnerProps) {
  const [testSuites, setTestSuites] = useState<TestSuite[]>([
    {
      id: "1",
      name: "Component Tests",
      description: "Unit tests for React components",
      totalTests: 15,
      passedTests: 12,
      failedTests: 2,
      skippedTests: 1,
      duration: 2.3,
      status: "completed",
      results: [
        {
          id: "1-1",
          name: "ThemeToggle renders correctly",
          status: "passed",
          duration: 0.1,
          category: "unit",
          timestamp: new Date()
        },
        {
          id: "1-2",
          name: "CollaborationPanel handles user interactions",
          status: "passed",
          duration: 0.2,
          category: "unit",
          timestamp: new Date()
        },
        {
          id: "1-3",
          name: "VoiceSearch recognizes speech input",
          status: "failed",
          duration: 1.5,
          error: "Speech recognition not supported in test environment",
          category: "unit",
          timestamp: new Date()
        }
      ]
    },
    {
      id: "2",
      name: "Integration Tests",
      description: "API integration and data flow tests",
      totalTests: 8,
      passedTests: 7,
      failedTests: 1,
      skippedTests: 0,
      duration: 4.1,
      status: "completed",
      results: [
        {
          id: "2-1",
          name: "Search query submission",
          status: "passed",
          duration: 0.8,
          category: "integration",
          timestamp: new Date()
        },
        {
          id: "2-2",
          name: "Collaboration session management",
          status: "failed",
          duration: 2.1,
          error: "WebSocket connection timeout",
          category: "integration",
          timestamp: new Date()
        }
      ]
    },
    {
      id: "3",
      name: "E2E Tests",
      description: "End-to-end user journey tests",
      totalTests: 5,
      passedTests: 4,
      failedTests: 1,
      skippedTests: 0,
      duration: 12.5,
      status: "running",
      results: [
        {
          id: "3-1",
          name: "Complete search workflow",
          status: "passed",
          duration: 3.2,
          category: "e2e",
          timestamp: new Date()
        },
        {
          id: "3-2",
          name: "Theme switching",
          status: "running",
          duration: 0,
          category: "e2e",
          timestamp: new Date()
        }
      ]
    },
    {
      id: "4",
      name: "Visual Regression Tests",
      description: "UI consistency and visual changes",
      totalTests: 12,
      passedTests: 10,
      failedTests: 2,
      skippedTests: 0,
      duration: 8.7,
      status: "completed",
      results: [
        {
          id: "4-1",
          name: "Search page layout",
          status: "passed",
          duration: 1.1,
          category: "visual",
          timestamp: new Date()
        },
        {
          id: "4-2",
          name: "Dark mode styling",
          status: "failed",
          duration: 0.9,
          error: "Color contrast ratio below WCAG standards",
          category: "visual",
          timestamp: new Date()
        }
      ]
    }
  ]);

  const [isRunning, setIsRunning] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedSuite, setSelectedSuite] = useState<string | null>(null);

  // Simulate test execution
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        setTestSuites(prev => prev.map(suite => {
          if (suite.status === "running") {
            // Simulate test progress
            const updatedResults = suite.results.map(result => {
              if (result.status === "running") {
                return {
                  ...result,
                  status: Math.random() > 0.7 ? "passed" : "running",
                  duration: result.duration + 0.1
                };
              }
              return result;
            });

            const allCompleted = updatedResults.every(r => r.status !== "running");
            const passedCount = updatedResults.filter(r => r.status === "passed").length;
            const failedCount = updatedResults.filter(r => r.status === "failed").length;

            return {
              ...suite,
              results: updatedResults,
              passedTests: passedCount,
              failedTests: failedCount,
              status: allCompleted ? "completed" : "running",
              duration: suite.duration + 0.1
            };
          }
          return suite;
        }));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const startAllTests = useCallback(() => {
    setIsRunning(true);
    setTestSuites(prev => prev.map(suite => ({
      ...suite,
      status: "running",
      results: suite.results.map(result => ({
        ...result,
        status: "running",
        duration: 0
      }))
    })));
  }, []);

  const stopTests = useCallback(() => {
    setIsRunning(false);
    setTestSuites(prev => prev.map(suite => ({
      ...suite,
      status: suite.status === "running" ? "failed" : suite.status
    })));
  }, []);

  const resetTests = useCallback(() => {
    setIsRunning(false);
    setTestSuites(prev => prev.map(suite => ({
      ...suite,
      status: "idle",
      results: suite.results.map(result => ({
        ...result,
        status: "pending",
        duration: 0,
        error: undefined
      }))
    })));
  }, []);

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

  const totalTests = testSuites.reduce((sum, suite) => sum + suite.totalTests, 0);
  const totalPassed = testSuites.reduce((sum, suite) => sum + suite.passedTests, 0);
  const totalFailed = testSuites.reduce((sum, suite) => sum + suite.failedTests, 0);
  const totalSkipped = testSuites.reduce((sum, suite) => sum + suite.skippedTests, 0);
  const totalDuration = testSuites.reduce((sum, suite) => sum + suite.duration, 0);

  return (
    <div className={cn("relative", className)}>
      {/* Test Runner Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        className={cn(
          "fixed bottom-32 right-4 z-50 rounded-full w-12 h-12 p-0",
          "bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:bg-white dark:hover:bg-slate-800",
          "transition-all duration-300 hover:scale-110",
          "shadow-lg hover:shadow-xl"
        )}
      >
        <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        {totalFailed > 0 && (
          <Badge 
            variant="secondary" 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-red-500 text-white"
          >
            {totalFailed}
          </Badge>
        )}
      </Button>

      {/* Test Runner Panel */}
      {isOpen && (
        <div className="fixed bottom-44 right-4 z-40 w-96 max-h-[80vh] overflow-hidden">
          <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardHeader className="pb-3 border-b border-gray-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Test Runner
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {totalPassed}/{totalTests} passed
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
                {/* Test Controls */}
                <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                  <div className="flex items-center space-x-2 mb-3">
                    <Button
                      size="sm"
                      onClick={isRunning ? stopTests : startAllTests}
                      disabled={testSuites.every(s => s.status === "completed")}
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
                          Run All Tests
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={resetTests}
                    >
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Overall Progress */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Overall Progress</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {Math.round((totalPassed / totalTests) * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={(totalPassed / totalTests) * 100} 
                      className="h-2"
                    />
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>Duration: {totalDuration.toFixed(1)}s</span>
                      <span>Passed: {totalPassed} | Failed: {totalFailed} | Skipped: {totalSkipped}</span>
                    </div>
                  </div>
                </div>

                {/* Test Suites */}
                <div className="p-4 space-y-3">
                  {testSuites.map((suite) => (
                    <div
                      key={suite.id}
                      className="border border-gray-200 dark:border-slate-700 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(suite.status)}
                          <div>
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                              {suite.name}
                            </h4>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {suite.description}
                            </p>
                          </div>
                        </div>
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs", getStatusColor(suite.status))}
                        >
                          {suite.status}
                        </Badge>
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600 dark:text-gray-400">Progress</span>
                          <span className="text-gray-900 dark:text-white">
                            {suite.passedTests}/{suite.totalTests}
                          </span>
                        </div>
                        <Progress 
                          value={(suite.passedTests / suite.totalTests) * 100} 
                          className="h-1"
                        />
                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                          <span>{suite.duration.toFixed(1)}s</span>
                          <span>
                            {suite.passedTests} passed, {suite.failedTests} failed
                          </span>
                        </div>
                      </div>

                      {/* Detailed Results */}
                      {showDetails && (
                        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-slate-700">
                          <div className="space-y-2">
                            {suite.results.map((result) => (
                              <div
                                key={result.id}
                                className="flex items-center justify-between text-xs p-2 rounded bg-gray-50 dark:bg-slate-700/50"
                              >
                                <div className="flex items-center space-x-2">
                                  {getStatusIcon(result.status)}
                                  <span className="text-gray-700 dark:text-gray-300">
                                    {result.name}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                  <Badge 
                                    variant="outline" 
                                    className={cn("text-xs", getStatusColor(result.status))}
                                  >
                                    {result.category}
                                  </Badge>
                                  <span className="text-gray-500 dark:text-gray-400">
                                    {result.duration.toFixed(1)}s
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export function useTestRunner() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleTestRunner = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    toggleTestRunner,
  };
}
