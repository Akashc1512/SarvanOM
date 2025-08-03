"use client";

import React, { useState } from "react";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { useToast } from "@/hooks/useToast";
import { LoadingSpinner } from "@/ui/atoms/loading-spinner";
import { Search, Sparkles, AlertCircle } from "lucide-react";
import { api, type QueryResponse, type Source } from "@/services/api";

interface QueryInputProps {
  onQuerySubmit?: (query: QueryResponse) => void;
  onQueryUpdate?: (query: QueryResponse) => void;
  className?: string;
}

export const QueryInput: React.FC<QueryInputProps> = ({
  onQuerySubmit,
  onQueryUpdate,
  className
}) => {
  const { toast } = useToast();
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string>("");
  const [sources, setSources] = useState<Source[]>([]);

  const handleSubmit = async () => {
    if (!inputValue.trim() || loading) return;

    setLoading(true);
    try {
      const data = await api.submitComprehensiveQuery(inputValue);
      
      // Update local state
      setAnswer(data.answer || "");
      setSources(data.sources || []);
      
      // Call callbacks
      onQuerySubmit?.(data);
      onQueryUpdate?.(data);
      
      toast({
        title: "Query submitted successfully",
        description: "Your comprehensive query has been processed",
      });
    } catch (error: any) {
      console.error("Query submission error:", error);
      
      let errorMessage = "Failed to submit query";
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.code === "NETWORK_ERROR") {
        errorMessage = "Network error. Please check your connection and try again.";
      } else if (error.code === "TIMEOUT") {
        errorMessage = "Request timed out. Please try again.";
      }
      
      toast({
        title: "Query Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`space-y-6 ${className || ""}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Comprehensive Research Query
          </CardTitle>
          <CardDescription>
            Ask any question and get AI-powered research with fact-checking and citations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Input
                type="text"
                placeholder="What would you like to research? (e.g., 'What are the latest developments in quantum computing?')"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                className="text-lg"
                aria-label="Research query input"
                aria-describedby="query-help"
              />
              <p id="query-help" className="text-sm text-gray-500">
                Be specific in your questions for better results. This query will include fact-checking and citations.
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleSubmit}
                disabled={!inputValue.trim() || loading}
                className="flex-1"
                aria-describedby="submit-help"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" color="white" />
                    <span className="ml-2">Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Research with AI
                  </>
                )}
              </Button>
            </div>
            <p id="submit-help" className="text-sm text-gray-500">
              Click to start comprehensive AI-powered research with fact-checking
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Research Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-gray-600" role="list">
            <li role="listitem">
              • Be specific in your questions for better results
            </li>
            <li role="listitem">
              • Include context or background information when relevant
            </li>
            <li role="listitem">
              • Ask follow-up questions to dive deeper into topics
            </li>
            <li role="listitem">
              • Use the feedback system to improve future responses
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}; 