"use client";

import React, { useState } from "react";
import { QueryForm } from "@/ui/QueryForm";
import { AnswerDisplay } from "@/ui/AnswerDisplay";
import { SourcesList } from "@/ui/SourcesList";
import { type QueryResponse, type Source } from "@/services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Search, Sparkles, Globe } from "lucide-react";
import { useQueryStore } from "@/state/query-store";

export default function ComprehensiveQueryPage() {
  const { currentQuery } = useQueryStore();
  const [answer, setAnswer] = useState<string>("");
  const [sources, setSources] = useState<Source[]>([]);

  // Update local state when query store changes
  React.useEffect(() => {
    if (currentQuery) {
      setAnswer(currentQuery.answer || "");
      setSources(currentQuery.sources || []);
    }
  }, [currentQuery]);

  const handleQuerySubmit = (query: QueryResponse) => {
    setAnswer(query.answer || "");
    setSources(query.sources || []);
  };

  const handleQueryUpdate = (query: QueryResponse) => {
    setAnswer(query.answer || "");
    setSources(query.sources || []);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Comprehensive Research Query
        </h1>
        <p className="text-lg text-gray-600">
          Advanced AI-powered research with fact-checking and citations
        </p>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-blue-600" />
              Smart Query Processing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Advanced query understanding with context-aware processing
            </CardDescription>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              Fact-Checking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Automated fact verification with confidence scoring
            </CardDescription>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-green-600" />
              Citation Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Automatic source citation with inline references
            </CardDescription>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Query Input */}
        <div>
          <QueryForm
            onQuerySubmit={handleQuerySubmit}
            onQueryUpdate={handleQueryUpdate}
          />
        </div>

        {/* Results Display */}
        <div className="space-y-6">
          {/* Answer Display */}
          {currentQuery && (
            <AnswerDisplay query={currentQuery} />
          )}

          {/* Standalone Sources List */}
          {sources.length > 0 && !currentQuery && (
            <SourcesList sources={sources} />
          )}

          {/* Instructions */}
          {!currentQuery && sources.length === 0 && (
            <Card>
              <CardHeader>
                <CardTitle>How to Use</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm text-gray-600">
                  <p>1. Enter your research question in the input field</p>
                  <p>2. Click &quot;Research with AI&quot; to submit your query</p>
                  <p>3. Wait for the comprehensive analysis to complete</p>
                  <p>4. Review the answer with inline citations [1], [2], etc.</p>
                  <p>5. Check the sources list for detailed references</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
} 