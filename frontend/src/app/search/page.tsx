"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Sparkles, Zap, Brain, Globe, Mic } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";
import { Card, CardContent } from "@/ui/ui/card";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { SearchSuggestions } from "@/ui/SearchSuggestions";
import { VoiceSearch } from "@/ui/VoiceSearch";
import { StarField, NebulaEffect } from "@/ui/CosmicParticles";
import { ThemeSelector } from "@/ui/ThemeSelector";
import { useToast } from "@/hooks/useToast";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSubmitting(true);
    setShowSuggestions(false);
    
    try {
      // Navigate to results page with the query
      router.push(`/search/results?q=${encodeURIComponent(query.trim())}`);
    } catch (error) {
      toast({
        title: "Search Error",
        description: "Failed to submit your query. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    // Auto-submit the suggestion
    router.push(`/search/results?q=${encodeURIComponent(suggestion.trim())}`);
  };

  const handleVoiceTranscript = (transcript: string) => {
    setQuery(transcript);
    toast({
      title: "Voice Input",
      description: "Query captured from voice input. Click Search to proceed.",
      variant: "default",
    });
  };

  const exampleQueries = [
    "What are the latest developments in quantum computing?",
    "How does climate change affect marine ecosystems?",
    "Explain the history of artificial intelligence",
    "What are the benefits of renewable energy sources?",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      {/* Advanced cosmic background effects */}
      <StarField />
      <NebulaEffect />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Sparkles className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              SarvanOM
            </h1>
          </div>
          <div className="flex items-center space-x-3">
            <ThemeSelector />
            <ThemeToggle size="sm" />
          </div>
        </div>

        {/* Main Search Interface */}
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8">
            <h2 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-gray-900 via-purple-800 to-blue-900 dark:from-white dark:via-purple-200 dark:to-blue-200 bg-clip-text text-transparent">
              Universal Knowledge
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Ask anything. Get intelligent, verified answers from across the cosmos of knowledge.
            </p>
          </div>

          {/* Search Form */}
          <Card className="max-w-2xl mx-auto mb-8 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Ask anything about the universe..."
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setShowSuggestions(e.target.value.length > 0);
                    }}
                    onFocus={() => setShowSuggestions(query.length > 0)}
                    className="pl-10 pr-12 py-3 text-lg border-purple-200 dark:border-purple-700 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-purple-500/20 dark:bg-slate-700/50"
                    disabled={isSubmitting}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <VoiceSearch
                      onTranscript={handleVoiceTranscript}
                      size="sm"
                      className="ml-2"
                    />
                  </div>
                  <SearchSuggestions
                    query={query}
                    isVisible={showSuggestions}
                    onSuggestionSelect={handleSuggestionSelect}
                    onClose={() => setShowSuggestions(false)}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={!query.trim() || isSubmitting}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Searching the cosmos...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Zap className="h-5 w-5" />
                      <span>Search</span>
                    </div>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Example Queries */}
          <div className="max-w-3xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Try these examples:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(example)}
                  className="text-left p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50 hover:bg-white/80 dark:hover:bg-slate-800/80 transition-all duration-200 hover:scale-105 text-sm text-gray-700 dark:text-gray-300"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Features */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50">
              <Brain className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">AI-Powered</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Advanced AI models provide intelligent, contextual responses
              </p>
            </div>
            <div className="text-center p-6 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50">
              <Globe className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Multi-Source</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Verified information from diverse, reliable sources
              </p>
            </div>
            <div className="text-center p-6 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50">
              <Sparkles className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Cosmic Fast</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Lightning-fast responses with real-time processing
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
