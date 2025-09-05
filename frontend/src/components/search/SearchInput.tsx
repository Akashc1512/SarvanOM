"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { MagnifyingGlassIcon, SparklesIcon, PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";
import { useSearchSessionStore } from "@/lib/store";

interface SearchInputProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
  isLoading?: boolean;
}

export function SearchInput({ 
  onSearch, 
  placeholder = "Ask anything about knowledge, research, or insights...",
  className,
  isLoading = false
}: SearchInputProps) {
  const [query, setQuery] = useState("");
  const storeLoading = useSearchSessionStore((s) => s.isLoading);
  const disabled = isLoading || storeLoading;
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSearch(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("w-full max-w-4xl mx-auto", className)}
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          {/* Search Input */}
          <div className={cn(
            "cosmic-search-container relative flex items-center transition-all duration-300",
            isFocused 
              ? "cosmic-glow-primary border-cosmic-border-accent" 
              : "border-cosmic-border-primary hover:border-cosmic-border-accent"
          )}>
            {/* Search Icon */}
            <div className="pl-6 pr-4">
              <MagnifyingGlassIcon className="w-6 h-6 cosmic-text-tertiary" />
            </div>

            {/* Input Field */}
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              disabled={disabled}
              aria-label="Search query"
              className="cosmic-search-input flex-1 bg-transparent text-lg py-6 pr-20 focus:outline-none disabled:opacity-50"
            />

            {/* AI Indicator */}
            <div className="absolute right-4 flex items-center gap-2">
              <SparklesIcon className="w-5 h-5 text-cosmic-primary-500" />
              
              {/* Submit Button */}
              <button
                type="submit"
                disabled={!query.trim() || disabled}
                className={cn(
                  "p-2 rounded-xl transition-all duration-200 flex items-center justify-center cosmic-hover-lift",
                  query.trim() && !isLoading
                    ? "cosmic-btn-primary cosmic-glow-soft"
                    : "bg-cosmic-bg-secondary text-cosmic-text-tertiary cursor-not-allowed"
                )}
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <PaperAirplaneIcon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Focus Ring */}
          {isFocused && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute inset-0 rounded-2xl bg-cosmic-primary-500/10 border-2 border-cosmic-primary-500/30 pointer-events-none cosmic-glow-soft"
            />
          )}
        </div>

        {/* Search Suggestions */}
        {isFocused && !query && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 cosmic-card p-4"
          >
            <p className="text-sm cosmic-text-tertiary mb-3">Try asking about:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                "What are the latest developments in AI?",
                "How does quantum computing work?",
                "Explain machine learning algorithms",
                "What is the future of renewable energy?"
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion)}
                  className="cosmic-nav-item text-left p-2 rounded-lg text-sm"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </form>
    </motion.div>
  );
}
