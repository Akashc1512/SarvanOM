"use client";

import { useCallback, useRef } from "react";
import { useSearchSessionStore } from "@/lib/store";
import { toast } from "sonner";

interface UseSearchOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

export function useSearch(options: UseSearchOptions = {}) {
  const {
    queryText,
    setQueryText,
    setAnswerContent,
    setCitations,
    setLoading,
    setSearchError,
    resetSession,
  } = useSearchSessionStore();

  const eventSourceRef = useRef<EventSource | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    // Reset previous session
    resetSession();
    setQueryText(query);
    setLoading(true);
    setSearchError("");

    try {
      // Close any existing SSE connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }

      // Abort any existing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      // Step 1: Call the search endpoint to get initial results
      const searchResponse = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
        signal: abortControllerRef.current.signal,
      });

      if (!searchResponse.ok) {
        throw new Error(`Search failed: ${searchResponse.statusText}`);
      }

      const searchData = await searchResponse.json();
      
      // Set initial citations if available
      if (searchData.citations) {
        setCitations(searchData.citations);
      }

      // Step 2: Start SSE streaming for the answer
      const backendUrl = process.env['NEXT_PUBLIC_BACKEND_URL'] || "http://localhost:8000";
      const streamUrl = `${backendUrl}/stream/search?query=${encodeURIComponent(query)}`;
      
      const eventSource = new EventSource(streamUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log("SSE connection opened");
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleStreamEvent(data);
        } catch (error) {
          console.error("Error parsing SSE data:", error);
        }
      };

      eventSource.onerror = (error) => {
        console.error("SSE error:", error);
        setSearchError("Connection lost. Please try again.");
        setLoading(false);
        eventSource.close();
        eventSourceRef.current = null;
      };

    } catch (error) {
      console.error("Search error:", error);
      const errorMessage = error instanceof Error ? error.message : "Search failed";
      setSearchError(errorMessage);
      setLoading(false);
      
      if (options.onError) {
        options.onError(errorMessage);
      }
      
      toast.error("Search failed. Please try again.");
    }
  }, [setQueryText, setAnswerContent, setCitations, setLoading, setSearchError, resetSession, options]);

  const handleStreamEvent = useCallback((data: any) => {
    switch (data.event) {
      case "content_chunk":
        setAnswerContent((prev: string) => prev + data.text);
        break;
      
      case "context":
        if (data.sources) {
          setCitations(data.sources);
        }
        break;
      
      case "citations":
        if (data.citations) {
          setCitations(data.citations);
        }
        break;
      
      case "complete":
        setLoading(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        
        if (options.onSuccess) {
          options.onSuccess(data);
        }
        break;
      
      case "error":
        setSearchError(data.error_message || "Streaming error occurred");
        setLoading(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        break;
      
      case "heartbeat":
        // Keep connection alive
        break;
      
      default:
        console.log("Unknown event type:", data.event);
    }
  }, [setAnswerContent, setCitations, setLoading, setSearchError, options]);

  const stopSearch = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    setLoading(false);
  }, [setLoading]);

  const clearSearch = useCallback(() => {
    stopSearch();
    resetSession();
  }, [stopSearch, resetSession]);

  return {
    queryText,
    startSearch,
    stopSearch,
    clearSearch,
  };
}
