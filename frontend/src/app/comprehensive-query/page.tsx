"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { QueryForm } from "@/ui/QueryForm";
import { AnswerDisplay } from "@/ui/AnswerDisplay";
import { CitationPanel } from "@/ui/CitationPanel";
import { KnowledgeGraphPanel } from "@/ui/KnowledgeGraphPanel";
import { 
  BookOpen, 
  Search, 
  Brain, 
  MessageSquare, 
  Clock, 
  Network, 
  BarChart3,
  Zap,
  Target,
  Lightbulb,
  TrendingUp,
  Shield,
  Users,
  Globe,
  Database,
  FileText
} from "lucide-react";
import { type QueryResponse } from "@/services/api";

const exampleQueries = [
  {
    title: "Market Research Analysis",
    description: "Comprehensive analysis of market trends, competitors, and opportunities",
    query: "Analyze the current market trends in artificial intelligence, including key players, emerging technologies, market size, and future projections. Include competitive analysis and investment patterns.",
    features: ["Multi-source", "Analytics", "Citations", "Graph"]
  },
  {
    title: "Academic Literature Review",
    description: "In-depth review of academic papers and research findings",
    query: "Conduct a comprehensive literature review on machine learning applications in healthcare, focusing on recent developments, challenges, and future directions. Include peer-reviewed sources and clinical studies.",
    features: ["Academic", "Citations", "Analysis", "Graph"]
  },
  {
    title: "Technical Documentation Research",
    description: "Research technical specifications and implementation details",
    query: "Research the latest developments in React 18 features, including concurrent rendering, automatic batching, and new hooks. Include code examples and migration guides.",
    features: ["Technical", "Code", "Documentation", "Examples"]
  },
  {
    title: "Business Strategy Analysis",
    description: "Strategic analysis of business opportunities and challenges",
    query: "Analyze the business strategy of Tesla in the electric vehicle market, including their competitive advantages, market positioning, challenges, and future outlook. Include financial analysis and industry trends.",
    features: ["Business", "Strategy", "Financial", "Analysis"]
  }
];

export default function ComprehensiveQueryPage() {
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [queryHistory, setQueryHistory] = useState<QueryResponse[]>([]);
  const [showCitations, setShowCitations] = useState(false);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client side
  useState(() => {
    setIsClient(true);
  });

  const handleQuerySubmit = async (query: QueryResponse) => {
    setCurrentQuery(query);
    setQueryHistory(prev => [query, ...prev.slice(0, 9)]); // Keep last 10 queries
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setCurrentQuery(query);
  };

  const handleFeedback = (
    rating: number,
    helpful: boolean,
    feedback?: string,
  ) => {
    console.log("Feedback received:", { rating, helpful, feedback });
    // Here you would typically send feedback to your analytics service
  };

  const handleOpenAnalytics = () => {
    if (isClient && typeof window !== "undefined") {
      window.open('/analytics', '_blank');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Comprehensive Query System
          </h1>
          <p className="text-gray-600">
            Advanced research and analysis with multi-source intelligence
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Query Interface */}
          <div className="lg:col-span-2 space-y-6">
            <QueryForm 
              onQuerySubmit={handleQuerySubmit}
              onQueryUpdate={handleQueryUpdate}
            />

            {currentQuery && (
              <AnswerDisplay 
                query={currentQuery} 
                onFeedback={handleFeedback}
              />
            )}

            {currentQuery && showCitations && currentQuery.citations && (
              <CitationPanel sources={currentQuery.citations.map(citation => ({
                title: citation.title || citation.text,
                url: citation.url || "",
                snippet: citation.text,
                source_type: "web",
                relevance_score: 0.8,
                credibility_score: 0.8
              }))} />
            )}

            {currentQuery && showKnowledgeGraph && (
              <KnowledgeGraphPanel 
                query={currentQuery.query_id || ""}
              />
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Features Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Advanced Features
                </CardTitle>
                <CardDescription>
                  Comprehensive research capabilities
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
                    <Target className="h-4 w-4 text-purple-600" />
                    <span className="text-sm">Precision targeting</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm">Insight generation</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-orange-600" />
                    <span className="text-sm">Trend analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-red-600" />
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
                    <Database className="h-4 w-4 text-gray-600" />
                    <span className="text-sm">Knowledge base</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-pink-600" />
                    <span className="text-sm">Document analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-pink-600" />
                    <span className="text-sm">Interactive feedback</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Example Queries */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Example Queries
                </CardTitle>
                <CardDescription>
                  Try these comprehensive research examples
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {exampleQueries.map((example, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h4 className="font-medium text-sm mb-2">{example.title}</h4>
                      <p className="text-xs text-gray-600 mb-3">{example.description}</p>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {example.features.map((feature, featureIndex) => (
                          <Badge key={featureIndex} variant="outline" className="text-xs">
                            {feature}
                          </Badge>
                        ))}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => {
                          // This would trigger the query form with the example
                          console.log("Example query:", example.query);
                        }}
                      >
                        Try This Query
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
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
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={handleOpenAnalytics}
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Analytics
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 