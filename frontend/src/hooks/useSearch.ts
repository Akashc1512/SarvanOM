/**
 * useSearch Hook
 * 
 * React hook for managing search functionality.
 * Handles search queries, suggestions, and result management.
 */

import { useState, useCallback, useEffect } from 'react';

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

interface SearchResponse {
  items: SearchResult[];
  total: number;
  query: string;
  searchTime: number;
}

interface UseSearchReturn {
  searchResults: SearchResult[];
  searchSuggestions: string[];
  isLoading: boolean;
  error: string | null;
  performSearch: (query: string) => Promise<SearchResponse>;
  clearResults: () => void;
  getSuggestions: (query: string) => Promise<string[]>;
}

export const useSearch = (): UseSearchReturn => {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Perform search
  const performSearch = useCallback(async (query: string): Promise<SearchResponse> => {
    if (!query.trim()) {
      return { items: [], total: 0, query, searchTime: 0 };
    }

    setIsLoading(true);
    setError(null);

    try {
      const startTime = Date.now();
      
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Search API error: ${response.status}`);
      }

      const data = await response.json();
      const searchTime = Date.now() - startTime;

      const searchResponse: SearchResponse = {
        items: data.results || [],
        total: data.total || 0,
        query,
        searchTime
      };

      setSearchResults(searchResponse.items);
      return searchResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Search failed';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get search suggestions
  const getSuggestions = useCallback(async (query: string): Promise<string[]> => {
    if (!query.trim() || query.length < 2) {
      setSearchSuggestions([]);
      return [];
    }

    try {
      const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`Suggestions API error: ${response.status}`);
      }

      const data = await response.json();
      const suggestions = data.suggestions || [];
      
      setSearchSuggestions(suggestions);
      return suggestions;
    } catch (error) {
      console.error('Failed to get search suggestions:', error);
      setSearchSuggestions([]);
      return [];
    }
  }, []);

  // Clear search results
  const clearResults = useCallback(() => {
    setSearchResults([]);
    setSearchSuggestions([]);
    setError(null);
  }, []);

  // Debounced suggestions
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchResults.length > 0) {
        // Generate suggestions based on current results
        const suggestions = searchResults
          .slice(0, 5)
          .map(result => result.title)
          .filter((title, index, array) => array.indexOf(title) === index);
        
        setSearchSuggestions(suggestions);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchResults]);

  return {
    searchResults,
    searchSuggestions,
    isLoading,
    error,
    performSearch,
    clearResults,
    getSuggestions,
  };
};

export default useSearch;