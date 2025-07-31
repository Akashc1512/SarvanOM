"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { QueryForm } from "@/components/QueryForm";
import { AnswerDisplay } from "@/components/AnswerDisplay";
import { TaskList } from "@/components/TaskList";
import { type QueryResponse } from "@/lib/api";
import {
  Search,
  Sparkles,
  TrendingUp,
  Clock,
  Star,
  MessageSquare,
  Zap,
  Globe,
  BookOpen,
  Users,
  BarChart3,
} from "lucide-react";

export default function Dashboard() {
  const { toast } = useToast();
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [recentQueries, setRecentQueries] = useState<QueryResponse[]>([]);

  const handleQuerySubmit = async (query: QueryResponse) => {
    setCurrentQuery(query);
    // Add to recent queries
    setRecentQueries((prev) => [query, ...prev.slice(0, 4)]);
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setCurrentQuery(query);
    // Update in recent queries
    setRecentQueries((prev) =>
      prev.map((q) => (q.query_id === query.query_id ? query : q)),
    );
  };

  const handleFeedback = (
    rating: number,
    helpful: boolean,
    feedback?: string,
  ) => {
    console.log("Feedback submitted:", { rating, helpful, feedback });
    // Analytics tracking could be added here
  };

  // Mock data for demonstration
  const platformStats = {
    totalQueries: 1247,
    activeUsers: 23,
    aiInteractions: 156,
    avgResponseTime: "2.3s",
  };

  const quickActions = [
    {
      title: "Market Research",
      description: "Analyze market trends and competitive landscape",
      icon: TrendingUp,
      query: "What are the latest trends in renewable energy markets?",
    },
    {
      title: "Technical Analysis",
      description: "Get detailed technical explanations",
      icon: Zap,
      query: "How does quantum computing work and what are its applications?",
    },
    {
      title: "Academic Research",
      description: "Find academic sources and papers",
      icon: BookOpen,
      query: "What are the recent developments in machine learning algorithms?",
    },
    {
      title: "Industry Insights",
      description: "Get industry-specific analysis",
      icon: Globe,
      query: "What are the key challenges facing the healthcare industry?",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Universal Knowledge Hub
        </h1>
        <p className="text-xl text-gray-600">
          AI-powered research platform combining search, synthesis, and
          collaboration
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Search Interface */}
          <QueryForm
            onQuerySubmit={handleQuerySubmit}
            onQueryUpdate={handleQueryUpdate}
          />

          {/* Results Display */}
          {currentQuery && (
            <AnswerDisplay query={currentQuery} onFeedback={handleFeedback} />
          )}

          {/* Task Generation */}
          {currentQuery && currentQuery.answer && (
            <TaskList
              answer={currentQuery.answer}
              query={currentQuery.query_id}
              onTasksGenerated={(tasks) => {
                console.log("Tasks generated:", tasks);
                // Analytics tracking could be added here
              }}
            />
          )}

          {/* Quick Actions */}
          {!currentQuery && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  Quick Research Actions
                </CardTitle>
                <CardDescription>
                  Start with these popular research topics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className="h-auto p-4 justify-start text-left"
                      onClick={() => {
                        // This would trigger a new query
                        toast({
                          title: "Quick Action",
                          description: `Research: ${action.title}`,
                        });
                      }}
                    >
                      <div className="flex items-start gap-3">
                        <action.icon className="h-5 w-5 text-blue-500 mt-0.5" />
                        <div>
                          <div className="font-medium">{action.title}</div>
                          <div className="text-sm text-gray-500">
                            {action.description}
                          </div>
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Platform Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Platform Stats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Queries</span>
                  <span className="font-medium">
                    {platformStats.totalQueries.toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Users</span>
                  <span className="font-medium">
                    {platformStats.activeUsers}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">AI Interactions</span>
                  <span className="font-medium">
                    {platformStats.aiInteractions}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Avg Response</span>
                  <span className="font-medium">
                    {platformStats.avgResponseTime}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Queries */}
          {recentQueries.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recent Queries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentQueries.map((query) => (
                    <div
                      key={query.query_id}
                      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setCurrentQuery(query)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          setCurrentQuery(query);
                        }
                      }}
                      role="button"
                      tabIndex={0}
                    >
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {query.query_id}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(query.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            query.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : query.status === "processing"
                                ? "bg-blue-100 text-blue-800"
                                : query.status === "failed"
                                  ? "bg-red-100 text-red-800"
                                  : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {query.status}
                        </span>
                        {query.confidence && (
                          <span className="text-xs text-gray-500">
                            {(query.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Platform Features
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-blue-500" />
                  <span>Multi-source search</span>
                </div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-green-500" />
                  <span>AI synthesis</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-purple-500" />
                  <span>Real-time collaboration</span>
                </div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-orange-500" />
                  <span>Expert review system</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
