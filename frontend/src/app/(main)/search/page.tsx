/**
 * Search Page - SarvanOM v2
 * 
 * Main search interface with Guided Prompt integration.
 * Follows Cosmic Pro design system with accessibility features.
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Send, 
  Loader2, 
  Filter, 
  Settings, 
  History, 
  Star,
  ExternalLink,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Share2,
  Bookmark
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { designTokens } from '@/lib/design-tokens';
import GuidedPromptModal from '@/components/GuidedPromptModal';
import { useGuidedPrompt } from '@/hooks/useGuidedPrompt';
import { useSearch } from '@/hooks/useSearch';

interface SearchResult {
  id: string;
  title: string;
  content: string;
  source: string;
  url: string;
  relevance_score: number;
  timestamp: string;
  type: 'web' | 'document' | 'knowledge' | 'news';
}

interface SearchState {
  query: string;
  results: SearchResult[];
  isLoading: boolean;
  error: string | null;
  hasSearched: boolean;
  totalResults: number;
  searchTime: number;
}

export default function SearchPage() {
  const [searchState, setSearchState] = useState<SearchState>({
    query: '',
    results: [],
    isLoading: false,
    error: null,
    hasSearched: false,
    totalResults: 0,
    searchTime: 0
  });

  const [showFilters, setShowFilters] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Guided Prompt integration
  const {
    isGuidedPromptEnabled,
    showGuidedPrompt,
    guidedPromptData,
    handleGuidedPromptAccept,
    handleGuidedPromptEdit,
    handleGuidedPromptSkip,
    handleGuidedPromptClose
  } = useGuidedPrompt();

  // Search hook
  const { performSearch, searchSuggestions } = useSearch();

  // Focus search input on mount
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, []);

  // Load search history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('sarvanom-search-history');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }

    const savedFavorites = localStorage.getItem('sarvanom-search-favorites');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Handle search submission
  const handleSearch = async (query: string, skipGuidedPrompt = false) => {
    if (!query.trim()) return;

    // Show Guided Prompt if enabled and not skipped
    if (isGuidedPromptEnabled && !skipGuidedPrompt) {
      // This would trigger the Guided Prompt modal
      // For now, we'll proceed with the search
    }

    setSearchState(prev => ({
      ...prev,
      query,
      isLoading: true,
      error: null,
      hasSearched: true
    }));

    try {
      const startTime = Date.now();
      const results = await performSearch(query);
      const searchTime = Date.now() - startTime;

      setSearchState(prev => ({
        ...prev,
        results: results.items,
        totalResults: results.total,
        searchTime,
        isLoading: false
      }));

      // Add to search history
      const newHistory = [query, ...searchHistory.filter(h => h !== query)].slice(0, 10);
      setSearchHistory(newHistory);
      localStorage.setItem('sarvanom-search-history', JSON.stringify(newHistory));

      // Scroll to results
      if (resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (error) {
      setSearchState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Search failed',
        isLoading: false
      }));
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(searchState.query);
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch(searchState.query);
    }
  };

  // Toggle favorite
  const toggleFavorite = (query: string) => {
    const newFavorites = favorites.includes(query)
      ? favorites.filter(f => f !== query)
      : [...favorites, query];
    setFavorites(newFavorites);
    localStorage.setItem('sarvanom-search-favorites', JSON.stringify(newFavorites));
  };

  // Copy result to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Show toast notification
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Search</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                aria-label="Search history"
              >
                <History className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                aria-label="Search filters"
              >
                <Filter className="w-5 h-5" />
              </button>
              <button
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                aria-label="Search settings"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchState.query}
                onChange={(e) => setSearchState(prev => ({ ...prev, query: e.target.value }))}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything... (e.g., 'What is quantum computing?')"
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                aria-label="Search query"
              />
              <button
                type="submit"
                disabled={searchState.isLoading || !searchState.query.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Search"
              >
                {searchState.isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>

          {/* Search Suggestions */}
          <AnimatePresence>
            {searchSuggestions.length > 0 && searchState.query && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-2 bg-white border border-gray-200 rounded-lg shadow-lg"
              >
                {searchSuggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSearch(suggestion)}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Search className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-700">{suggestion}</span>
                    </div>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Search History Sidebar */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            className="fixed left-0 top-0 h-full w-80 bg-white border-r border-gray-200 shadow-lg z-20"
          >
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Search History</h3>
            </div>
            <div className="p-4 space-y-2">
              {searchHistory.map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleSearch(query)}
                  className="w-full flex items-center justify-between p-2 text-left hover:bg-gray-50 rounded-md transition-colors"
                >
                  <span className="text-gray-700 truncate">{query}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(query);
                    }}
                    className="p-1 text-gray-400 hover:text-yellow-500 transition-colors"
                  >
                    <Star className={cn(
                      "w-4 h-4",
                      favorites.includes(query) ? "fill-yellow-400 text-yellow-400" : ""
                    )} />
                  </button>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Results */}
        {searchState.hasSearched && (
          <motion.div
            ref={resultsRef}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {searchState.totalResults.toLocaleString()} results
                </h2>
                <p className="text-sm text-gray-600">
                  Found in {searchState.searchTime}ms for "{searchState.query}"
                </p>
              </div>
            </div>

            {/* Error State */}
            {searchState.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{searchState.error}</p>
              </div>
            )}

            {/* Results List */}
            <div className="space-y-4">
              {searchState.results.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {result.title}
                      </h3>
                      <p className="text-gray-700 mb-3 line-clamp-3">
                        {result.content}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => copyToClipboard(result.content)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                        aria-label="Copy content"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                        aria-label="Share result"
                      >
                        <Share2 className="w-4 h-4" />
                      </button>
                      <button
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                        aria-label="Bookmark result"
                      >
                        <Bookmark className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <ExternalLink className="w-4 h-4" />
                        {result.source}
                      </span>
                      <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                      <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                        {result.type}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        className="p-1 text-gray-400 hover:text-green-600 hover:bg-green-100 rounded transition-colors"
                        aria-label="Like result"
                      >
                        <ThumbsUp className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded transition-colors"
                        aria-label="Dislike result"
                      >
                        <ThumbsDown className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!searchState.hasSearched && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-12 h-12 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start your search
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Ask questions, search for information, or explore topics. 
              Our AI will help you find the most relevant results.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {['What is machine learning?', 'Latest news about AI', 'How does quantum computing work?'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSearch(suggestion)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Guided Prompt Modal */}
      <GuidedPromptModal
        isOpen={showGuidedPrompt}
        originalQuery={guidedPromptData?.originalQuery || ''}
        refinements={guidedPromptData?.refinements || []}
        constraints={guidedPromptData?.constraints || []}
        onAccept={handleGuidedPromptAccept}
        onEdit={handleGuidedPromptEdit}
        onSkip={handleGuidedPromptSkip}
        onClose={handleGuidedPromptClose}
        isLoading={false}
        deviceType="desktop"
        language="en"
      />
    </div>
  );
}