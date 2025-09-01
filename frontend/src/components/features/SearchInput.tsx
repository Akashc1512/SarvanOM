"use client";

import React, { useState, useRef, useEffect } from "react";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useSearchSessionStore } from "@/lib/store";
import { useSearch } from "@/hooks/useSearch";
import { toast } from "sonner";

interface SearchInputProps {
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  autoFocus?: boolean;
}

export function SearchInput({ 
  placeholder = "Ask a question or search...",
  className = "",
  disabled = false,
  autoFocus = false
}: SearchInputProps) {
  const [localQuery, setLocalQuery] = useState("");
  const { isLoading, queryText } = useSearchSessionStore();
  const { startSearch } = useSearch();
  const inputRef = useRef<HTMLInputElement>(null);
  
  const isDisabled = disabled || isLoading;

  // Sync with global store query text
  useEffect(() => {
    if (queryText && queryText !== localQuery) {
      setLocalQuery(queryText);
    }
  }, [queryText, localQuery]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!localQuery.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    if (isDisabled) {
      return;
    }

    try {
      await startSearch(localQuery.trim());
    } catch (error) {
      console.error("Search submission error:", error);
      toast.error("Failed to start search. Please try again.");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSearchButtonClick = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
    handleSubmit(new Event('submit') as any);
  };

  return (
    <form onSubmit={handleSubmit} className={`w-full ${className}`}>
      <div className="relative">
        {/* Search Icon */}
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon 
            className="h-5 w-5 text-gray-400 dark:text-gray-500" 
            aria-hidden="true" 
          />
        </div>
        
        {/* Input Field */}
        <input
          ref={inputRef}
          type="search"
          value={localQuery}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          disabled={isDisabled}
          placeholder={placeholder}
          aria-label="Search query"
          autoFocus={autoFocus}
          autoComplete="off"
          spellCheck="false"
          className="w-full rounded-md bg-input pl-10 pr-12 p-3 text-base text-primary-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 border border-border hover:border-primary/50 focus:border-primary"
        />
        
        {/* Loading Indicator or Submit Button */}
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          {isLoading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent" />
          ) : (
            <button
              type="submit"
              disabled={isDisabled || !localQuery.trim()}
              onClick={handleSearchButtonClick}
              aria-label="Submit search"
              className="p-1 rounded-md hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              <MagnifyingGlassIcon 
                className="h-4 w-4 text-gray-400 dark:text-gray-500 hover:text-primary transition-colors duration-200" 
                aria-hidden="true"
              />
            </button>
          )}
        </div>
      </div>
      
      {/* Search Status */}
      {isLoading && (
        <div className="mt-2 text-sm text-muted-foreground flex items-center">
          <div className="animate-spin rounded-full h-3 w-3 border border-primary border-t-transparent mr-2" />
          Searching the cosmos for answers...
        </div>
      )}
    </form>
  );
}
