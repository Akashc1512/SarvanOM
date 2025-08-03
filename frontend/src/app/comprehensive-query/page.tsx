"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Textarea } from "@/ui/ui/textarea";
import { Label } from "@/ui/ui/label";
import { QueryForm } from "@/ui/QueryForm";
import { AnswerDisplay } from "@/ui/AnswerDisplay";
import { CitationPanel } from "@/ui/CitationPanel";
import { ExpertValidationButton } from "@/ui/ExpertValidationButton";
import { KnowledgeGraphVisualization } from "@/ui/KnowledgeGraphVisualization";
import { 
  Search, 
  BookOpen, 
  Shield, 
  Network, 
  BarChart3,
  ArrowLeft,
  Sparkles,
  CheckCircle,
  Clock,
  Brain,
  MessageSquare
} from "lucide-react";
import Link from "next/link";
import { type QueryResponse } from "@/services/api";

export default function ComprehensiveQueryPage() {
  const [currentQuery, setCurrentQuery] = useState<QueryResponse | null>(null);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [showCitations, setShowCitations] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleQuerySubmit = async (query: QueryResponse) => {
    setIsProcessing(true);
    setCurrentQuery(query);
    // Simulate processing time
    setTimeout(() => {
      setIsProcessing(false);
    }, 2000);
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setCurrentQuery(query);
  };

  const handleFeedback = (
    rating: number,
    helpful: boolean,
    feedback?: string,
  ) => {
    console.log("Feedback submitted:", { rating, helpful, feedback });
  };

  const exampleQueries = [
    {
      title: "AI Impact on Jobs",
      description: "Comprehensive analysis of AI's effect on employment",
      query: "What is the current state of AI's impact on job markets, and what are the most reliable predictions for the next decade? Include recent studies and expert opinions.",
      features: ["Citations", "Expert Validation", "Knowledge Graph"]
    },
    {
      title: "Climate Change Solutions",
      description: "Evidence-based climate change mitigation strategies",
      query: "What are the most effective and scientifically validated strategies for addressing climate change? Include cost-benefit analyses and implementation timelines.",
      features: ["Fact-Checking", "Academic Sources", "Expert Validation"]
    },
    {
      title: "Quantum Computing",
      description: "Technical deep-dive into quantum computing",
      query: "How does quantum computing work, what are its current limitations, and when can we expect practical applications? Include technical details and industry timelines.",
      features: ["Technical Analysis", "Expert Validation", "Knowledge Graph"]
    }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Comprehensive Research Query</h1>
          </div>
          <p className="text-gray-600">
            Advanced AI-powered research with automatic fact-checking, citations, and expert validation
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            AI-Powered
          </Badge>
          <Badge variant="outline" className="flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Fact-Checked
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Query Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Query Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Research Query
              </CardTitle>
              <CardDescription>
                Ask complex questions and get comprehensive answers with citations and validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <QueryForm
                onQuerySubmit={handleQuerySubmit}
                onQueryUpdate={handleQueryUpdate}
              />
            </CardContent>
          </Card>

          {/* Processing Status */}
          {isProcessing && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center gap-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">Processing comprehensive research...</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Answer Display */}
          {currentQuery && !isProcessing && (
            <AnswerDisplay
              query={currentQuery}
              onFeedback={handleFeedback}
            />
          )}

          {/* Knowledge Graph Visualization */}
          {currentQuery && showKnowledgeGraph && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="h-5 w-5" />
                  Knowledge Graph
                </CardTitle>
                <CardDescription>
                  Visualize relationships and entities from your query
                </CardDescription>
              </CardHeader>
              <CardContent>
                <KnowledgeGraphVisualization
                  query={currentQuery.answer || ""}
                  maxNodes={30}
                  maxEdges={50}
                  height="500px"
                  showControls={false}
                  onNodeClick={(node) => {
                    console.log("Node clicked:", node);
                  }}
                  onEdgeClick={(edge) => {
                    console.log("Edge clicked:", edge);
                  }}
                />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Features Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Research Features
              </CardTitle>
              <CardDescription>
                Advanced capabilities available
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Multi-source citations</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <span className="text-sm">Expert validation</span>
                </div>
                <div className="flex items-center gap-2">
                  <Network className="h-4 w-4 text-purple-600" />
                  <span className="text-sm">Knowledge graph</span>
                </div>
                <div className="flex items-center gap-2">
                  <Brain className="h-4 w-4 text-orange-600" />
                  <span className="text-sm">AI-powered analysis</span>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-indigo-600" />
                  <span className="text-sm">Academic sources</span>
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
                  onClick={() => {
                    // This would open the analytics page
                    window.open('/analytics', '_blank');
                  }}
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
  );
} 