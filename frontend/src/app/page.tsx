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
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { QueryForm } from "@/components/QueryForm";
import { AnswerDisplay } from "@/components/AnswerDisplay";
import { TaskList } from "@/components/TaskList";
import { ConversationContext } from "@/components/ConversationContext";
import { LLMProviderBadge } from "@/components/LLMProviderBadge";
import { KnowledgeGraphPanel } from "@/components/KnowledgeGraphPanel";
// import { CollaborativeEditor } from "@/components/CollaborativeEditor";
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
  Brain,
  Network,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const { toast } = useToast();
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [recentQueries, setRecentQueries] = useState<QueryResponse[]>([]);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);

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
        <p className="text-lg text-gray-600">
          Advanced AI-powered research and knowledge discovery platform
        </p>
      </div>

      {/* Platform Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{platformStats.totalQueries}</p>
                <p className="text-sm text-gray-600">Total Queries</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{platformStats.activeUsers}</p>
                <p className="text-sm text-gray-600">Active Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">{platformStats.aiInteractions}</p>
                <p className="text-sm text-gray-600">AI Interactions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-2xl font-bold">{platformStats.avgResponseTime}</p>
                <p className="text-sm text-gray-600">Avg Response</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Loader Demo Link */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            New: SarvanOM Loader Demo
          </CardTitle>
          <CardDescription>
            Check out our beautiful animated loader component
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Experience the new SarvanOM loader with orbiting nodes and smooth animations
            </p>
            <Link href="/loader-demo">
              <Button variant="outline" className="flex items-center gap-2">
                <ExternalLink className="h-4 w-4" />
                View Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Query Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Conversation Context */}
          <ConversationContext
            sessionId={sessionId}
            maxHistory={5}
            onContextSelect={handleContextSelect}
            onQueryReference={handleQueryReference}
          />

          {/* Query Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="h-5 w-5" />
                <span>Ask Your Question</span>
              </CardTitle>
              <CardDescription>
                Get comprehensive answers with citations and validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <QueryForm
                onQuerySubmit={handleQuerySubmit}
                onQueryUpdate={handleQueryUpdate}
              />
            </CardContent>
          </Card>

          {/* Answer Display */}
          {currentQuery && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5" />
                    <span>Answer</span>
                  </CardTitle>
                  <div className="flex items-center space-x-2">
                    {/* LLM Provider Badge */}
                    {currentQuery.llm_provider && (
                      <LLMProviderBadge
                        provider={currentQuery.llm_provider as any}
                        model={currentQuery.llm_model || "unknown"}
                        responseTime={currentQuery.processing_time || undefined}
                        confidence={currentQuery.confidence || undefined}
                      />
                    )}
                    {/* Knowledge Graph Toggle */}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowKnowledgeGraph(!showKnowledgeGraph)}
                    >
                      <Network className="h-4 w-4 mr-1" />
                      Knowledge Graph
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <AnswerDisplay
                  query={currentQuery}
                  onFeedback={handleFeedback}
                />
              </CardContent>
            </Card>
          )}

          {/* Knowledge Graph Panel */}
          {showKnowledgeGraph && (
            <KnowledgeGraphPanel
              query={currentQuery?.answer || ""}
              onEntityClick={handleEntityClick}
              onRelationshipClick={handleRelationshipClick}
              maxEntities={8}
              maxRelationships={12}
            />
          )}

          {/* Task List */}
          {currentQuery && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5" />
                  <span>Generated Tasks</span>
                </CardTitle>
                <CardDescription>
                  AI-generated tasks based on your query
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TaskList queryId={currentQuery.query_id} />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Quick Actions</span>
              </CardTitle>
              <CardDescription>
                Common research queries to get started
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start h-auto p-3"
                    onClick={() => {
                      // This could trigger a query with the suggested text
                      console.log("Quick action:", action.query);
                    }}
                  >
                    <action.icon className="h-4 w-4 mr-2" />
                    <div className="text-left">
                      <div className="font-medium text-sm">{action.title}</div>
                      <div className="text-xs text-gray-500">
                        {action.description}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Queries */}
          {recentQueries.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Recent Queries</span>
                </CardTitle>
                <CardDescription>
                  Your recent research questions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentQueries.slice(0, 3).map((query, index) => (
                    <div
                      key={index}
                      className="p-2 border border-gray-200 rounded text-sm cursor-pointer hover:bg-gray-50"
                      onClick={() => setCurrentQuery(query)}
                    >
                      <div className="font-medium line-clamp-2">
                        {query.answer?.substring(0, 100)}...
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(query.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Platform Features */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="h-5 w-5" />
                <span>Platform Features</span>
              </CardTitle>
              <CardDescription>
                Advanced capabilities available
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <Brain className="h-4 w-4 text-blue-600" />
                  <span>Multi-Agent AI Processing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Network className="h-4 w-4 text-green-600" />
                  <span>Knowledge Graph Integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4 text-purple-600" />
                  <span>Citation & Fact Checking</span>
                </div>
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4 text-orange-600" />
                  <span>Real-time Analytics</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
