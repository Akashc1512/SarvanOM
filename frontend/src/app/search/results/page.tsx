"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, ExternalLink, Copy, Share2, ThumbsUp, ThumbsDown, Sparkles, Download, FileText, BookOpen, CheckCircle, AlertCircle, Info } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { useToast } from "@/hooks/useToast";
import { CosmicLoader } from "@/ui/CosmicLoader";
import { MediaRenderer } from "@/ui/MediaRenderer";
import { PerformanceMonitor, usePerformanceMonitor } from "@/ui/PerformanceMonitor";
import { CacheManager } from "@/ui/CacheManager";
import { SourceCard } from "@/ui/SourceCard";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface SearchResult {
  query: string;
  answer: string;
  confidence?: number;
  processing_time?: number;
  citations?: Array<{
    marker: string;
    source: {
      title: string;
      url: string;
      snippet: string;
      source_type: string;
      relevance_score: number;
      credibility_score: number;
      domain?: string;
      provider?: string;
    };
    confidence: number;
    sentence_start: number;
    sentence_end: number;
    claim_type: string;
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
  sources?: Array<{
    title: string;
    url: string;
    snippet: string;
    domain: string;
    provider: string;
    metadata?: any;
  }>;
  bibliography?: Array<{
    marker: string;
    title: string;
    url: string;
    domain: string;
    provider: string;
    relevance_score: number;
    credibility_score: number;
  }>;
  uncertainty_flags?: string[];
  overall_confidence?: number;
}

interface StreamEvent {
  event: string;
  data: string;
}

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCitations, setShowCitations] = useState(true);
  const [streamedAnswer, setStreamedAnswer] = useState("");
  const [sources, setSources] = useState<any[]>([]);
  const [citations, setCitations] = useState<any[]>([]);
  const [bibliography, setBibliography] = useState<any[]>([]);
  const [uncertaintyFlags, setUncertaintyFlags] = useState<string[]>([]);
  const [overallConfidence, setOverallConfidence] = useState<number>(0);
  const [streamId, setStreamId] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const { toast } = useToast();
  const { isOpen: isPerformanceMonitorOpen, togglePerformanceMonitor } = usePerformanceMonitor();

  // Mock metrics for now - in real implementation this would come from the backend
  const metrics = {
    processing_time: 0,
    tokens_generated: 0,
    cache_hits: 0,
    llm_calls: 0
  };

  useEffect(() => {
    if (!query) {
      setError("No query provided");
      setIsLoading(false);
      return;
    }

    startStreamingSearch();
  }, [query]);

  useEffect(() => {
    // Cleanup event source on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const startStreamingSearch = async () => {
    if (!query) return;

    setIsLoading(true);
    setIsStreaming(true);
    setError(null);
    setStreamedAnswer("");
    setSources([]);
    setCitations([]);
    setBibliography([]);
    setUncertaintyFlags([]);
    setOverallConfidence(0);

    try {
      // Close any existing event source
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create new event source for streaming
      const backendUrl = process.env["NEXT_PUBLIC_BACKEND_URL"] || "http://localhost:8000";
      const streamUrl = `${backendUrl}/stream/search?query=${encodeURIComponent(query)}`;
      
      const eventSource = new EventSource(streamUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log("SSE connection opened");
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleStreamEvent(data);
        } catch (error) {
          console.error("Error parsing SSE data:", error);
        }
      };

      eventSource.onerror = (error) => {
        console.error("SSE error:", error);
        setError("Connection lost. Please try again.");
        setIsStreaming(false);
        eventSource.close();
      };

    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setIsStreaming(false);
    }
  };

  const handleStreamEvent = (data: any) => {
    switch (data.event) {
      case "content_chunk":
        setStreamedAnswer(prev => prev + data.text);
        break;
      
      case "context":
        // Handle initial context with sources
        if (data.sources) {
          setSources(data.sources);
        }
        break;
      
      case "citations":
        // Handle citation data
        if (data.citations) {
          setCitations(data.citations);
        }
        if (data.bibliography) {
          setBibliography(data.bibliography);
        }
        if (data.uncertainty_flags) {
          setUncertaintyFlags(data.uncertainty_flags);
        }
        if (data.overall_confidence) {
          setOverallConfidence(data.overall_confidence);
        }
        break;
      
      case "complete":
        setIsStreaming(false);
        setIsLoading(false);
        setStreamId(data.stream_id);
        
        // Set final result with enhanced data
        setResult({
          query: query!,
          answer: streamedAnswer + data.text,
          confidence: data.confidence || overallConfidence || 0.85,
          processing_time: data.duration_seconds * 1000,
          sources: data.sources || sources,
          citations: data.citations || citations,
          bibliography: data.bibliography || bibliography,
          uncertainty_flags: data.uncertainty_flags || uncertaintyFlags,
          overall_confidence: data.overall_confidence || overallConfidence,
          query_id: data.stream_id
        });
        
        // Note: completeProcessing function would be implemented for analytics tracking
        console.log("Stream completed", {
          confidence: data.confidence || overallConfidence || 0.85,
          duration: data.duration_seconds * 1000,
          method: "streaming",
          tokens: data.total_tokens || 0
        });
        
        // Close event source
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }
        break;
      
      case "error":
        setError(data.error_message || "Streaming error occurred");
        setIsStreaming(false);
        setIsLoading(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }
        break;
      
      case "heartbeat":
        // Keep connection alive
        break;
      
      default:
        console.log("Unknown event type:", data.event);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied!",
        description: "Answer copied to clipboard",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy to clipboard",
        variant: "destructive",
      });
    }
  };

  const exportToMarkdown = () => {
    if (!result) return;

    let markdown = `# ${result.query}\n\n`;

    // Add confidence and uncertainty info
    if (result.overall_confidence) {
      markdown += `**Confidence:** ${(result.overall_confidence * 100).toFixed(1)}%\n\n`;
    }

    if (result.uncertainty_flags && result.uncertainty_flags.length > 0) {
      markdown += `**Uncertainty Flags:**\n`;
      result.uncertainty_flags.forEach(flag => {
        markdown += `- ${flag}\n`;
      });
      markdown += `\n`;
    }

    // Add the answer with citation markers
    markdown += `${result.answer}\n\n`;

    // Add bibliography
    if (result.bibliography && result.bibliography.length > 0) {
      markdown += `## Sources\n\n`;
      result.bibliography.forEach((source, index) => {
        markdown += `${source.marker}. [${source.title}](${source.url}) - ${source.domain} (${source.provider})\n`;
        if (source.relevance_score) {
          markdown += `   - Relevance: ${(source.relevance_score * 100).toFixed(0)}%\n`;
        }
        if (source.credibility_score) {
          markdown += `   - Credibility: ${(source.credibility_score * 100).toFixed(0)}%\n`;
        }
        markdown += `\n`;
      });
    }

    markdown += `---\n*Generated by SarvanOM - ${new Date().toISOString()}`;

    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sarvanom-${query?.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Exported!",
      description: "Answer exported as Markdown with citations",
      variant: "default",
    });
  };

  const exportToNotion = () => {
    if (!result) return;

    // Create Notion-compatible markdown
    let notionMarkdown = `# ${result.query}\n\n`;

    // Add confidence info
    if (result.overall_confidence) {
      notionMarkdown += `**Confidence:** ${(result.overall_confidence * 100).toFixed(1)}%\n\n`;
    }

    // Add the answer
    notionMarkdown += `${result.answer}\n\n`;

    // Add sources in Notion format
    if (result.bibliography && result.bibliography.length > 0) {
      notionMarkdown += `## Sources\n\n`;
      result.bibliography.forEach((source) => {
        notionMarkdown += `- [${source.title}](${source.url}) (${source.domain})\n`;
      });
    }

    notionMarkdown += `\n---\n*Generated by SarvanOM*`;

    copyToClipboard(notionMarkdown);
    toast({
      title: "Ready for Notion!",
      description: "Answer copied in Notion format. Paste into Notion to import.",
      variant: "default",
    });
  };

  const handleFeedback = (isPositive: boolean) => {
    toast({
      title: isPositive ? "Thanks!" : "Feedback received",
      description: isPositive ? "We're glad this helped!" : "We'll work to improve this answer.",
      variant: "default",
    });
  };

  const renderAnswerWithCitations = (answer: string, citations: any[]) => {
    if (!citations || citations.length === 0) {
      return answer;
    }

    // Create a map of citation markers to source info
    const citationMap = new Map();
    citations.forEach(citation => {
      citationMap.set(citation.marker, citation);
    });

    // Split the answer into parts and render with citation markers
    const parts = answer.split(/(\[\d+\])/);
    
    return parts.map((part, index) => {
      if (citationMap.has(part)) {
        const citation = citationMap.get(part);
        return (
          <span key={index} className="inline-flex items-center">
            <span className="text-blue-600 dark:text-blue-400 font-medium cursor-pointer hover:underline">
              {part}
            </span>
            <span className="ml-1 text-xs text-gray-500 dark:text-gray-400">
              ({citation.source.domain})
            </span>
          </span>
        );
      }
      return part;
    });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <div className="mb-6">
              <Link href="/search">
                <Button variant="outline" className="mb-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Search
                </Button>
              </Link>
            </div>
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-red-200/50 dark:border-red-800/50">
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold text-red-600 dark:text-red-400 mb-2">
                  Search Error
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4">{error}</p>
                <Button onClick={startStreamingSearch} className="w-full">
                  Try Again
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link href="/search">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                SarvanOM
              </h1>
            </div>
          </div>
          <ThemeToggle size="sm" />
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Query Display */}
          <Card className="mb-6 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                {query}
              </h2>
              {isStreaming && (
                <div className="flex items-center space-x-2 text-sm text-purple-600 dark:text-purple-400">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                  <span>Generating answer...</span>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Answer */}
            <div className="lg:col-span-2">
              <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
                <CardHeader>
                  <CardTitle className="text-xl text-gray-900 dark:text-white flex items-center justify-between">
                    <span>Answer</span>
                    <div className="flex items-center space-x-2">
                      {result && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copyToClipboard(result.answer)}
                          >
                            <Copy className="h-4 w-4 mr-1" />
                            Copy
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={exportToMarkdown}
                          >
                            <FileText className="h-4 w-4 mr-1" />
                            Export MD
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={exportToNotion}
                          >
                            <BookOpen className="h-4 w-4 mr-1" />
                            Notion
                          </Button>
                        </>
                      )}
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  {isLoading ? (
                    <div className="space-y-4">
                      <CosmicLoader />
                      <p className="text-gray-600 dark:text-gray-300 text-center">
                        Searching the cosmos for answers...
                      </p>
                    </div>
                  ) : (
                    <div className="prose prose-gray dark:prose-invert max-w-none">
                      <div className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
                        {result && result.citations && result.citations.length > 0
                          ? renderAnswerWithCitations(streamedAnswer || result.answer || "", result.citations)
                          : (streamedAnswer || result?.answer || "")
                        }
                      </div>
                      
                      {isStreaming && (
                        <div className="flex items-center space-x-2 text-sm text-purple-600 dark:text-purple-400 mt-4">
                          <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                          <span>Streaming...</span>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Confidence and Uncertainty Info */}
              {result && (result.overall_confidence || (result.uncertainty_flags && result.uncertainty_flags.length > 0)) && (
                <Card className="mt-4 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border-gray-200/50 dark:border-slate-700/50">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        {result.overall_confidence && (
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                            <span className="text-sm text-gray-600 dark:text-gray-300">
                              Overall Confidence: <span className="font-medium">{(result.overall_confidence * 100).toFixed(1)}%</span>
                            </span>
                          </div>
                        )}
                        {result.uncertainty_flags && result.uncertainty_flags.length > 0 && (
                          <div className="flex items-start space-x-2">
                            <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                            <div className="text-sm text-gray-600 dark:text-gray-300">
                              <span className="font-medium">Uncertainty Flags:</span>
                              <ul className="mt-1 space-y-1">
                                {result.uncertainty_flags.map((flag, index) => (
                                  <li key={index} className="text-xs">• {flag}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Feedback */}
              {result && !isStreaming && (
                <Card className="mt-4 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border-gray-200/50 dark:border-slate-700/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        Was this answer helpful?
                      </span>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleFeedback(true)}
                        >
                          <ThumbsUp className="h-4 w-4 mr-1" />
                          Yes
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleFeedback(false)}
                        >
                          <ThumbsDown className="h-4 w-4 mr-1" />
                          No
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Bibliography */}
              {result && result.bibliography && result.bibliography.length > 0 && (
                <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
                  <CardHeader>
                    <CardTitle className="text-lg text-gray-900 dark:text-white flex items-center space-x-2">
                      <BookOpen className="h-5 w-5" />
                      <span>Sources ({result.bibliography.length})</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      {result.bibliography.map((source, index) => (
                        <SourceCard
                          key={index}
                          source={source}
                          showMarker={true}
                          compact={true}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Performance Metrics */}
              <PerformanceMonitor />

              {/* Cache Status */}
              <CacheManager onCacheHit={() => console.log("Cache hit")} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
