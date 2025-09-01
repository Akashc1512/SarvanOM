"use client";

import { useState, useEffect } from "react";
import { Search, Sparkles, Zap, Mic, X, Menu, ArrowLeft } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";
import { Card, CardContent } from "@/ui/ui/card";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { SearchSuggestions } from "@/ui/SearchSuggestions";
import { VoiceSearch } from "@/ui/VoiceSearch";
import { useToast } from "@/hooks/useToast";

interface MobileOptimizedSearchProps {
  onSearch: (query: string) => void;
  onBack?: () => void;
  showBackButton?: boolean;
  placeholder?: string;
  className?: string;
}

export function MobileOptimizedSearch({
  onSearch,
  onBack,
  showBackButton = false,
  placeholder = "Ask anything about the universe...",
  className = ""
}: MobileOptimizedSearchProps) {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const { toast } = useToast();

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSubmitting(true);
    setShowSuggestions(false);
    
    try {
      onSearch(query.trim());
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
    onSearch(suggestion.trim());
  };

  const handleVoiceTranscript = (transcript: string) => {
    setQuery(transcript);
    toast({
      title: "Voice Input",
      description: "Query captured from voice input. Click Search to proceed.",
      variant: "default",
    });
  };

  const clearQuery = () => {
    setQuery("");
    setShowSuggestions(false);
  };

  const exampleQueries = [
    "What are the latest developments in quantum computing?",
    "How does climate change affect marine ecosystems?",
    "Explain the history of artificial intelligence",
    "What are the benefits of renewable energy sources?",
  ];

  // Mobile-optimized search interface
  if (isMobile) {
    return (
      <div className={`w-full ${className}`}>
        {/* Mobile Header */}
        <div className="flex items-center justify-between p-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border-b border-gray-200 dark:border-slate-700">
          {showBackButton ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBack}
              className="p-2"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          ) : (
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              <h1 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                SarvanOM
              </h1>
            </div>
          )}
          
          <div className="flex items-center space-x-2">
            <ThemeToggle size="sm" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="p-2"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Mobile Search Form */}
        <div className="p-4">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-lg">
            <CardContent className="p-4">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    type="text"
                    placeholder={placeholder}
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setShowSuggestions(e.target.value.length > 0);
                    }}
                    onFocus={() => setShowSuggestions(query.length > 0)}
                    className="pl-10 pr-20 py-4 text-base border-purple-200 dark:border-purple-700 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-purple-500/20 dark:bg-slate-700/50"
                    disabled={isSubmitting}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                    {query && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={clearQuery}
                        className="h-8 w-8 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                    <VoiceSearch
                      onTranscript={handleVoiceTranscript}
                      size="sm"
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
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Searching...</span>
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

          {/* Mobile Example Queries */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Try these examples:
            </h3>
            <div className="space-y-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(example)}
                  className="w-full text-left p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50 hover:bg-white/80 dark:hover:bg-slate-800/80 transition-all duration-200 text-sm text-gray-700 dark:text-gray-300"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Mobile Menu Overlay */}
        {showMobileMenu && (
          <div className="fixed inset-0 bg-black/50 z-50" onClick={() => setShowMobileMenu(false)}>
            <div className="absolute top-0 right-0 w-64 h-full bg-white dark:bg-slate-800 shadow-xl p-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Menu</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <div className="space-y-4">
                <Button variant="ghost" className="w-full justify-start">
                  Settings
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  Help
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  About
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Desktop search interface
  return (
    <div className={`w-full ${className}`}>
      <Card className="max-w-2xl mx-auto bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder={placeholder}
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

      {/* Desktop Example Queries */}
      <div className="max-w-3xl mx-auto mt-8">
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4 text-center">
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
    </div>
  );
}
