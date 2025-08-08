"use client";

import { useState, useEffect, useRef } from "react";
import { Search, TrendingUp, Clock, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/ui/ui/card";
import { cn } from "@/lib/utils";

interface Suggestion {
  id: string;
  text: string;
  type: "trending" | "recent" | "suggested";
  icon?: React.ReactNode;
}

interface SearchSuggestionsProps {
  query: string;
  isVisible: boolean;
  onSuggestionSelect: (suggestion: string) => void;
  onClose: () => void;
}

export function SearchSuggestions({ 
  query, 
  isVisible, 
  onSuggestionSelect, 
  onClose 
}: SearchSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Mock suggestions - in real app, these would come from API
  const mockSuggestions: Suggestion[] = [
    { id: "1", text: "What are the latest developments in quantum computing?", type: "trending", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "2", text: "How does climate change affect marine ecosystems?", type: "trending", icon: <TrendingUp className="h-4 w-4" /> },
    { id: "3", text: "Explain the history of artificial intelligence", type: "recent", icon: <Clock className="h-4 w-4" /> },
    { id: "4", text: "What are the benefits of renewable energy sources?", type: "recent", icon: <Clock className="h-4 w-4" /> },
    { id: "5", text: "How do neural networks work?", type: "suggested", icon: <Sparkles className="h-4 w-4" /> },
    { id: "6", text: "What is the future of space exploration?", type: "suggested", icon: <Sparkles className="h-4 w-4" /> },
  ];

  useEffect(() => {
    if (!isVisible || !query.trim()) {
      setSuggestions([]);
      setSelectedIndex(-1);
      return;
    }

    // Filter suggestions based on query
    const filtered = mockSuggestions.filter(suggestion =>
      suggestion.text.toLowerCase().includes(query.toLowerCase())
    );

    // Add query-based suggestions
    const queryBasedSuggestions: Suggestion[] = [
      { id: "query-1", text: `${query} - latest research`, type: "suggested", icon: <Sparkles className="h-4 w-4" /> },
      { id: "query-2", text: `${query} - benefits and challenges`, type: "suggested", icon: <Sparkles className="h-4 w-4" /> },
      { id: "query-3", text: `${query} - future developments`, type: "suggested", icon: <Sparkles className="h-4 w-4" /> },
    ];

    setSuggestions([...filtered, ...queryBasedSuggestions].slice(0, 8));
    setSelectedIndex(-1);
  }, [query, isVisible]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isVisible) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex(prev => 
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
          break;
        case "Enter":
          e.preventDefault();
          if (selectedIndex >= 0 && suggestions[selectedIndex]) {
            onSuggestionSelect(suggestions[selectedIndex].text);
          }
          break;
        case "Escape":
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isVisible, suggestions, selectedIndex, onSuggestionSelect, onClose]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    if (isVisible) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isVisible, onClose]);

  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "trending":
        return "text-orange-600 dark:text-orange-400";
      case "recent":
        return "text-blue-600 dark:text-blue-400";
      case "suggested":
        return "text-purple-600 dark:text-purple-400";
      default:
        return "text-gray-600 dark:text-gray-400";
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "trending":
        return "Trending";
      case "recent":
        return "Recent";
      case "suggested":
        return "Suggested";
      default:
        return "Suggestion";
    }
  };

  return (
    <div 
      ref={containerRef}
      className="absolute top-full left-0 right-0 z-50 mt-1"
    >
      <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
        <CardContent className="p-0">
          <div className="max-h-80 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <button
                key={suggestion.id}
                onClick={() => onSuggestionSelect(suggestion.text)}
                onMouseEnter={() => setSelectedIndex(index)}
                className={cn(
                  "w-full text-left p-3 hover:bg-purple-50 dark:hover:bg-slate-700/50 transition-colors duration-200",
                  "border-b border-gray-100 dark:border-slate-700 last:border-b-0",
                  selectedIndex === index && "bg-purple-50 dark:bg-slate-700/50"
                )}
              >
                <div className="flex items-start space-x-3">
                  <div className={cn("mt-0.5", getTypeColor(suggestion.type))}>
                    {suggestion.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-900 dark:text-gray-100 truncate">
                        {suggestion.text}
                      </p>
                      <span className={cn(
                        "text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-slate-700",
                        getTypeColor(suggestion.type)
                      )}>
                        {getTypeLabel(suggestion.type)}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
          
          {/* Footer */}
          <div className="p-3 border-t border-gray-100 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/50">
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>Use ↑↓ to navigate, Enter to select</span>
              <span>{suggestions.length} suggestions</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
