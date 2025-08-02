"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api } from "@/lib/api";
import {
  MessageSquare,
  Clock,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  History,
  Sparkles,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ConversationItem {
  query: string;
  answer: string;
  timestamp: string;
  confidence: number;
  query_id?: string;
  llm_provider?: string;
  processing_time?: number;
}

interface ConversationContextProps {
  sessionId: string;
  maxHistory?: number;
  onContextSelect?: (context: ConversationItem) => void;
  onQueryReference?: (query: string) => void;
  className?: string;
}

export function ConversationContext({
  sessionId,
  maxHistory = 5,
  onContextSelect,
  onQueryReference,
  className = "",
}: ConversationContextProps) {
  const { toast } = useToast();
  const [conversationHistory, setConversationHistory] = useState<ConversationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      loadConversationHistory();
    }
  }, [sessionId]);

  const loadConversationHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get session state which includes conversation history
      const sessionState = await api.getSessionState(sessionId);
      
      if (sessionState && sessionState.conversation_history) {
        const history = sessionState.conversation_history
          .slice(-maxHistory)
          .map((item: any) => ({
            query: item.query || "",
            answer: item.answer || "",
            timestamp: item.timestamp || new Date().toISOString(),
            confidence: item.confidence || 0.5,
            query_id: item.query_id,
            llm_provider: item.llm_provider,
            processing_time: item.processing_time,
          }));
        
        setConversationHistory(history);
      } else {
        setConversationHistory([]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load conversation history");
      toast({
        title: "Error",
        description: "Failed to load conversation history",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleContextSelect = (item: ConversationItem) => {
    onContextSelect?.(item);
    toast({
      title: "Context Selected",
      description: "Previous conversation context has been loaded",
    });
  };

  const handleQueryReference = (query: string) => {
    onQueryReference?.(query);
    toast({
      title: "Query Referenced",
      description: "Previous query has been loaded for editing",
    });
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "bg-green-100 text-green-800";
    if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getProviderIcon = (provider?: string) => {
    switch (provider?.toLowerCase()) {
      case "ollama":
        return <Sparkles className="h-3 w-3" />;
      case "openai":
        return <MessageSquare className="h-3 w-3" />;
      default:
        return <MessageSquare className="h-3 w-3" />;
    }
  };

  if (conversationHistory.length === 0 && !isLoading) {
    return null; // Don't show anything if no history
  }

  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <History className="h-4 w-4 text-gray-600" />
            <CardTitle className="text-sm font-medium">
              Conversation History
            </CardTitle>
            <Badge variant="secondary" className="text-xs">
              {conversationHistory.length}
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={loadConversationHistory}
              disabled={isLoading}
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </Button>
          </div>
        </div>
        <CardDescription className="text-xs">
          Previous queries and answers for context
        </CardDescription>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-4">
              <RefreshCw className="h-4 w-4 animate-spin text-gray-500" />
              <span className="ml-2 text-sm text-gray-500">Loading history...</span>
            </div>
          ) : error ? (
            <div className="text-sm text-red-600 py-2">{error}</div>
          ) : (
            <ScrollArea className="h-64">
              <div className="space-y-3">
                {conversationHistory.map((item, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Clock className="h-3 w-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(item.timestamp)}
                        </span>
                        {item.llm_provider && (
                          <div className="flex items-center space-x-1">
                            {getProviderIcon(item.llm_provider)}
                            <span className="text-xs text-gray-500">
                              {item.llm_provider}
                            </span>
                          </div>
                        )}
                      </div>
                      <Badge
                        variant="secondary"
                        className={`text-xs ${getConfidenceColor(item.confidence)}`}
                      >
                        {Math.round(item.confidence * 100)}%
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">Query:</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-4 px-2 text-xs"
                            onClick={() => handleQueryReference(item.query)}
                          >
                            Use
                          </Button>
                        </div>
                        <p className="text-sm text-gray-800 line-clamp-2">
                          {item.query}
                        </p>
                      </div>

                      <div>
                        <span className="text-xs font-medium text-gray-700">Answer:</span>
                        <p className="text-sm text-gray-600 line-clamp-3 mt-1">
                          {item.answer}
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-6 px-2 text-xs"
                          onClick={() => handleContextSelect(item)}
                        >
                          Use as Context
                        </Button>
                        {item.processing_time && (
                          <span className="text-xs text-gray-500">
                            {item.processing_time.toFixed(1)}s
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      )}
    </Card>
  );
} 