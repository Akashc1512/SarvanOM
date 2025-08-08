"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, ExternalLink, Copy, Share2, ThumbsUp, ThumbsDown, Sparkles } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { useToast } from "@/hooks/useToast";
import { CosmicLoader } from "@/ui/CosmicLoader";
import { MediaRenderer } from "@/ui/MediaRenderer";
import { PerformanceMonitor, usePerformanceMonitor } from "@/ui/PerformanceMonitor";
import { CacheManager } from "@/ui/CacheManager";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface SearchResult {
  query: string;
  answer: string;
  confidence?: number;
  processing_time?: number;
  citations?: Array<{
    title: string;
    url: string;
    snippet: string;
    source_type: string;
    relevance_score: number;
    credibility_score: number;
  }>;
  query_id?: string;
  media?: Array<{
    type: "image" | "video";
    url: string;
    alt?: string;
    title?: string;
    description?: string;
    thumbnail?: string;
  }>;
}

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCitations, setShowCitations] = useState(false);
  const { toast } = useToast();
  const { metrics, startProcessing, completeProcessing, setError: setPerformanceError } = usePerformanceMonitor();

  useEffect(() => {
    if (!query) {
      setError("No query provided");
      setIsLoading(false);
      return;
    }

    fetchSearchResult();
  }, [query]);

  const fetchSearchResult = async () => {
    if (!query) return;

    setIsLoading(true);
    setError(null);
    startProcessing();

    try {
      // Simulate API call - replace with actual backend endpoint
      const response = await fetch(`/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch search results");
      }

      const data = await response.json();
      setResult(data);
      completeProcessing(data.confidence || 0.85, data.processing_time || 1200, "llama2", 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setPerformanceError();
      // For demo purposes, show a mock result
      setResult({
        query: query,
        answer: `# Search Results for "${query}"

This is a **demonstration** of how SarvanOM would display search results. In a real implementation, this would contain the actual AI-generated answer based on your query.

## Key Features

- **Markdown Rendering**: This text is rendered using React Markdown
- **Citations**: Sources are displayed with relevance scores
- **Cosmic Theme**: Beautiful space-inspired design
- **Responsive**: Works perfectly on all devices

### Example Code Block

\`\`\`javascript
// This would be actual code from the answer
function searchKnowledge(query) {
  return fetch('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query })
  });
}
\`\`\`

> This is a blockquote showing how quoted content would appear.

The system provides **intelligent answers** with proper formatting and structure.`,
        confidence: 0.85,
        processing_time: 1200,
        citations: [
          {
            title: "Example Source 1",
            url: "https://example.com/source1",
            snippet: "This is an example citation that would appear in the sources panel.",
            source_type: "web",
            relevance_score: 0.9,
            credibility_score: 0.8,
          },
          {
            title: "Example Source 2", 
            url: "https://example.com/source2",
            snippet: "Another example citation showing how multiple sources are displayed.",
            source_type: "academic",
            relevance_score: 0.8,
            credibility_score: 0.9,
          },
        ],
        media: [
          {
            type: "image",
            url: "https://picsum.photos/400/300",
            alt: "Example image",
            title: "Sample Image",
            description: "This is an example image that would be displayed with the results."
          },
          {
            type: "video",
            url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            title: "Example Video",
            description: "This is an example video that would be embedded with the results."
          }
        ],
        query_id: "demo_query_123",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyAnswer = async () => {
    if (!result?.answer) return;
    
    try {
      await navigator.clipboard.writeText(result.answer);
      toast({
        title: "Copied!",
        description: "Answer copied to clipboard",
      });
    } catch (err) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy answer",
        variant: "destructive",
      });
    }
  };

  const shareResult = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({
        title: "Shared!",
        description: "Link copied to clipboard",
      });
    } catch (err) {
      toast({
        title: "Share Failed", 
        description: "Failed to copy link",
        variant: "destructive",
      });
    }
  };

  const handleFeedback = (helpful: boolean) => {
    toast({
      title: "Feedback Received",
      description: `Thank you for your feedback! Answer marked as ${helpful ? "helpful" : "not helpful"}.`,
    });
  };

  const handleCacheHit = (entry: any) => {
    setResult(entry);
    toast({
      title: "Cache Hit!",
      description: "Loaded result from cache for instant response.",
    });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <div className="mb-8">
              <CosmicLoader size="lg" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                🚧 Our AI is taking a break
              </h1>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                {error}
              </p>
              <div className="space-x-4">
                <Button onClick={() => window.history.back()}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Go Back
                </Button>
                <Button variant="outline" onClick={fetchSearchResult}>
                  Try Again
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      {/* Cosmic background effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-2 h-2 bg-purple-400/30 rounded-full animate-pulse" />
        <div className="absolute top-40 right-20 w-1 h-1 bg-blue-400/40 rounded-full animate-pulse delay-1000" />
        <div className="absolute bottom-40 left-1/4 w-1.5 h-1.5 bg-purple-300/50 rounded-full animate-pulse delay-2000" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link href="/search">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Search
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                SarvanOM
              </h1>
            </div>
          </div>
          <ThemeToggle size="sm" />
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Query Display */}
          {query && (
            <Card className="mb-6 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Your Query:
                </h2>
                <p className="text-gray-700 dark:text-gray-300 text-lg">
                  {query}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {isLoading && (
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardContent className="p-8">
                <CosmicLoader 
                  size="lg" 
                  text="Searching the cosmos... Our AI is analyzing your query and gathering knowledge from across the universe."
                />
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {result && !isLoading && (
            <div className="space-y-6">
              {/* Answer Card */}
              <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl text-gray-900 dark:text-white">
                      Answer
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                      {result.confidence && (
                        <Badge variant="outline" className="text-xs">
                          {Math.round(result.confidence * 100)}% Confidence
                        </Badge>
                      )}
                      {result.processing_time && (
                        <Badge variant="outline" className="text-xs">
                          {result.processing_time}ms
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      className="text-gray-800 dark:text-gray-200"
                    >
                      {result.answer}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={copyAnswer}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={shareResult}
                      >
                        <Share2 className="h-4 w-4 mr-2" />
                        Share
                      </Button>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFeedback(true)}
                      >
                        <ThumbsUp className="h-4 w-4 mr-2" />
                        Helpful
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFeedback(false)}
                      >
                        <ThumbsDown className="h-4 w-4 mr-2" />
                        Not Helpful
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Media Content */}
              {result.media && result.media.length > 0 && (
                <MediaRenderer media={result.media} />
              )}

              {/* Performance Monitor */}
              <PerformanceMonitor metrics={metrics} />

              {/* Citations */}
              {result.citations && result.citations.length > 0 && (
                <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
                  <CardHeader>
                    <CardTitle className="text-xl text-gray-900 dark:text-white">
                      Sources ({result.citations.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {result.citations.map((citation, index) => (
                        <div
                          key={index}
                          className="p-4 rounded-lg bg-gray-50 dark:bg-slate-700/50 border border-gray-200 dark:border-slate-600"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-gray-900 dark:text-white">
                              {citation.title}
                            </h4>
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="text-xs">
                                {Math.round(citation.relevance_score * 100)}% Relevant
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {Math.round(citation.credibility_score * 100)}% Credible
                              </Badge>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                            {citation.snippet}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                              {citation.source_type}
                            </span>
                            <a
                              href={citation.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 text-sm font-medium flex items-center"
                            >
                              Visit Source
                              <ExternalLink className="h-3 w-3 ml-1" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Cache Manager */}
          <CacheManager onCacheHit={handleCacheHit} />
        </div>
      </div>
    </div>
  );
}
