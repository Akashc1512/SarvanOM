"use client";

import { useState } from "react";
import { Button } from "@/ui/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { useToast } from "@/hooks/useToast";
import { QueryForm } from "@/ui/QueryForm";
import { AnswerDisplay } from "@/ui/AnswerDisplay";
import { TaskList } from "@/ui/TaskList";
import { ConversationContext } from "@/ui/ConversationContext";
import { LLMProviderBadge } from "@/ui/LLMProviderBadge";
import { KnowledgeGraphPanel } from "@/ui/KnowledgeGraphPanel";
import { CitationPanel } from "@/ui/CitationPanel";
import { ErrorBoundary } from "@/ui/ErrorBoundary";
import { useQuerySubmission, useQueryPolling } from "@/hooks/useQuerySubmission";
import { type QueryResponse } from "@/services/api";
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
  Brain,
  Network,
  ArrowRight,
  ExternalLink,
  Shield,
} from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const { toast } = useToast();
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [recentQueries, setRecentQueries] = useState<QueryResponse[]>([]);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [showCitations, setShowCitations] = useState(false);

  // Use React Query hooks for better data management
  const querySubmission = useQuerySubmission({
    onSuccess: (data) => {
      setCurrentQuery(data);
      setRecentQueries((prev) => [data, ...prev.slice(0, 4)]);
      toast({
        title: "Query Submitted",
        description: "Your query is being processed. You'll see results shortly.",
      });
    },
    onError: (error) => {
      toast({
        title: "Query Failed",
        description: error.message || "Failed to submit query. Please try again.",
        variant: "destructive",
      });
    },
  });

  // Poll for query updates if we have a query ID
  const queryPolling = useQueryPolling(currentQuery?.query_id || null);

  const handleQuerySubmit = async (query: QueryResponse | { query: string }) => {
    // If we already have a query response, just update the state
    if ('answer' in query && query.answer) {
      setCurrentQuery(query as QueryResponse);
      setRecentQueries((prev) => [query as QueryResponse, ...prev.slice(0, 4)]);
      return;
    }

    // Otherwise, submit the query
    try {
      const queryText = 'query' in query ? query.query : '';
      await querySubmission.mutateAsync({
        query: queryText,
      });
    } catch (error) {
      console.error("Query submission error:", error);
    }
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setCurrentQuery(query);
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
    toast({
      title: "Feedback Received",
      description: "Thank you for your feedback! It helps us improve our responses.",
    });
  };

  const handleContextSelect = (context: any) => {
    console.log("Context selected:", context);
    toast({
      title: "Context Loaded",
      description: "Previous conversation context has been loaded for the next query",
    });
  };

  const handleQueryReference = (query: string) => {
    console.log("Query referenced:", query);
    // This could be used to pre-fill the query form
  };

  const handleEntityClick = (entity: any) => {
    console.log("Entity clicked:", entity);
    toast({
      title: "Entity Selected",
      description: `Selected entity: ${entity.name} (${entity.type})`,
    });
  };

  const handleRelationshipClick = (relationship: any) => {
    console.log("Relationship clicked:", relationship);
    toast({
      title: "Relationship Selected",
      description: `Selected relationship: ${relationship.relationship_type}`,
    });
  };

  const isProcessing = querySubmission.isPending || (queryPolling.data && !queryPolling.data.answer) || false;

  return (
    <ErrorBoundary>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Universal Knowledge Platform
                </h1>
                <p className="text-gray-600">
                  Advanced AI-powered research and analysis platform
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <LLMProviderBadge provider="ollama" model="llama2" showDetails={false} />
                <Link href="/analytics">
                  <Button variant="outline" size="sm">
                    <BarChart3 className="mr-2 h-4 w-4" />
                    Analytics
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Query Interface */}
            <div className="lg:col-span-2 space-y-6">
              <QueryForm 
                onQuerySubmit={handleQuerySubmit}
                onQueryUpdate={handleQueryUpdate}
              />

              {/* Answer Display */}
              {currentQuery && (
                <AnswerDisplay 
                  query={currentQuery} 
                  onFeedback={handleFeedback}
                  isLoading={isProcessing}
                />
              )}

              {/* Citations Panel */}
              {currentQuery && showCitations && currentQuery.citations && (
                <CitationPanel 
                  sources={currentQuery.citations.map(citation => ({
                    title: citation.title || citation.text,
                    url: citation.url || "",
                    snippet: citation.text,
                    source_type: "web",
                    relevance_score: 0.8,
                    credibility_score: 0.8
                  }))} 
                />
              )}

              {/* Knowledge Graph Panel */}
              {currentQuery && showKnowledgeGraph && (
                <KnowledgeGraphPanel 
                  query={currentQuery.query_id || ""}
                />
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Quick Actions
                  </CardTitle>
                  <CardDescription>
                    Common research actions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => setShowCitations(!showCitations)}
                    >
                      <BookOpen className="h-4 w-4 mr-2" />
                      {showCitations ? "Hide" : "Show"} Citations
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => setShowKnowledgeGraph(!showKnowledgeGraph)}
                    >
                      <Network className="h-4 w-4 mr-2" />
                      {showKnowledgeGraph ? "Hide" : "Show"} Knowledge Graph
                    </Button>
                    <Link href="/analytics">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                      >
                        <BarChart3 className="h-4 w-4 mr-2" />
                        View Analytics
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              {/* Features Overview */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Platform Features
                  </CardTitle>
                  <CardDescription>
                    Advanced research capabilities
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Search className="h-4 w-4 text-blue-600" />
                      <span className="text-sm">Multi-source search</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-green-600" />
                      <span className="text-sm">AI-powered analysis</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-purple-600" />
                      <span className="text-sm">Fact verification</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-indigo-600" />
                      <span className="text-sm">Expert validation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-teal-600" />
                      <span className="text-sm">Web integration</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4 text-pink-600" />
                      <span className="text-sm">Interactive feedback</span>
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
                    <CardDescription>
                      Your recent research activity
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {recentQueries.slice(0, 3).map((query, index) => (
                        <div
                          key={query.query_id || index}
                          className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => setCurrentQuery(query)}
                        >
                          <p className="text-sm font-medium line-clamp-2">
                            {query.answer ? `${query.answer.substring(0, 50)}...` : "Recent Query"}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              {query.confidence ? `${(query.confidence * 100).toFixed(0)}%` : "N/A"}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {query.processing_time ? `${query.processing_time}ms` : ""}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Conversation Context */}
              <ConversationContext
                sessionId={sessionId}
                onContextSelect={handleContextSelect}
                onQueryReference={handleQueryReference}
              />

              {/* Task List */}
              <TaskList />

              {/* Knowledge Graph Panel */}
              <KnowledgeGraphPanel
                onEntityClick={handleEntityClick}
                onRelationshipClick={handleRelationshipClick}
              />
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
