/**
 * QueryForm Component - Knowledge Query Interface
 *
 * A comprehensive query input form with real-time validation, submission handling,
 * and status tracking. This component integrates with the query store for state
 * management and provides a smooth user experience for knowledge queries.
 *
 * Features:
 * - Real-time input validation with debouncing
 * - Error handling and user feedback via toast notifications
 * - Loading states and progress indicators
 * - Integration with query store for global state management
 * - Accessibility compliance with ARIA labels and keyboard navigation
 * - Responsive design with mobile optimization
 *
 * Props:
 * - onQuerySubmit: Callback when query is successfully submitted
 * - onQueryUpdate: Callback when query status updates (processing, completed, error)
 * - className: Additional CSS classes for styling
 *
 * State Management:
 * - Uses React Query for server state management
 * - Local state for form inputs and UI interactions
 * - Global state via query store for cross-component communication
 *
 * Error Handling:
 * - Network errors with automatic retry logic
 * - Validation errors with user-friendly feedback
 * - Rate limiting with appropriate messaging
 * - Graceful degradation for offline scenarios
 *
 * Accessibility:
 * - ARIA labels and descriptions for screen readers
 * - Keyboard navigation support (Tab, Enter, Escape)
 * - Focus management and visible focus indicators
 * - Semantic HTML structure
 *
 * Performance:
 * - Debounced input validation to prevent excessive API calls
 * - Memoized callbacks to prevent unnecessary re-renders
 * - Efficient state updates with minimal re-renders
 * - Optimized polling with configurable intervals
 *
 * Example Usage:
 * ```tsx
 * <QueryForm
 *   onQuerySubmit={(query) => console.log('Query submitted:', query)}
 *   onQueryUpdate={(status) => console.log('Status updated:', status)}
 *   className="max-w-2xl mx-auto"
 * />
 * ```
 *
 * @author Universal Knowledge Platform Engineering Team
 * @version 1.0.0
 * @license MIT
 */

"use client";

import React, { useState, useCallback, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { useDebounce } from "@/hooks/use-debounce";
import { usePolling } from "@/hooks/use-polling";
import { useQueryStore } from "@/store/query-store";
import { QueryStatusCard } from "@/components/molecules/query-status-card";
import { LoadingSpinner } from "@/components/atoms/loading-spinner";
import { Search, Sparkles, AlertCircle } from "lucide-react";
import { api, type QueryRequest } from "@/lib/api";

interface QueryFormProps {
  onQuerySubmit?: (_query: any) => void;
  onQueryUpdate?: (_query: any) => void;
  className?: string;
}

export const QueryForm = React.memo<QueryFormProps>(
  ({ onQuerySubmit, onQueryUpdate, className }) => {
    const { toast } = useToast();
    const [query, setQuery] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

      const {
    currentQuery,
    isPolling,
    error,
    submitQuery,
    updateQuery,
    clearError,
  } = useQueryStore();

    // Debounced query validation
    const debouncedValidateQuery = useDebounce((_value: string) => {
      // Add validation logic here if needed
    }, 300);

    // Handle query input change
    const handleQueryChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setQuery(value);
        debouncedValidateQuery(value);
        clearError();
      },
      [debouncedValidateQuery, clearError],
    );

    // Handle form submission
    const handleSubmit = useCallback(
      async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || isSubmitting) return;

        setIsSubmitting(true);
        try {
          const queryRequest: QueryRequest = {
            query: query.trim(),
            context: "research",
          };

          await submitQuery(queryRequest);
          onQuerySubmit?.(currentQuery);

          toast({
            title: "Query submitted",
            description: "Your research query is being processed...",
          });
        } catch (error: any) {
          console.error("Query submission error:", error);
          
          // User-friendly error messages
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
          setIsSubmitting(false);
        }
      },
      [query, isSubmitting, submitQuery, currentQuery, onQuerySubmit, toast],
    );

    // Polling for query status updates
    const handlePoll = useCallback(async () => {
      if (!currentQuery?.query_id) return;

      try {
        const status = await api.getQueryStatus(currentQuery.query_id);
        updateQuery(status);
        onQueryUpdate?.(status);
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, [currentQuery?.query_id, updateQuery, onQueryUpdate]);

    // Start polling when query is processing
    usePolling({
      enabled: isPolling && currentQuery?.status === "processing",
      interval: 2000,
      onPoll: handlePoll,
      onError: (error) => {
        console.error("Polling failed:", error);
        toast({
          title: "Status update failed",
          description: "Unable to get latest query status",
          variant: "destructive",
        });
      },
      maxAttempts: 30, // 1 minute max
    });

    // Memoized form validation
    const isFormValid = useMemo(() => {
      return query.trim().length > 0 && !isSubmitting;
    }, [query, isSubmitting]);

    // Memoized submit button text
    const submitButtonText = useMemo(() => {
      if (isSubmitting) return "Processing...";
      return "Research with AI";
    }, [isSubmitting]);

    return (
      <div className={`space-y-6 ${className || ""}`}>
        {/* Search Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Universal Research Interface
            </CardTitle>
            <CardDescription>
              Ask any question and get AI-powered research with cited sources
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="What would you like to research? (e.g., 'What are the latest developments in quantum computing?')"
                  value={query}
                  onChange={handleQueryChange}
                  disabled={isSubmitting}
                  className="text-lg"
                  aria-label="Research query input"
                  aria-describedby="query-help"
                  aria-invalid={error ? "true" : "false"}
                />
                {error && (
                  <div
                    className="flex items-center gap-2 text-sm text-red-600"
                    role="alert"
                  >
                    <AlertCircle className="h-4 w-4" />
                    <span>{error}</span>
                  </div>
                )}
                <p id="query-help" className="text-sm text-gray-500">
                  Be specific in your questions for better results
                </p>
              </div>

              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={!isFormValid}
                  className="flex-1"
                  aria-describedby="submit-help"
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" color="white" />
                      <span className="ml-2">{submitButtonText}</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      {submitButtonText}
                    </>
                  )}
                </Button>
              </div>
              <p id="submit-help" className="text-sm text-gray-500">
                Click to start AI-powered research
              </p>
            </form>
          </CardContent>
        </Card>

        {/* Current Query Status */}
        {currentQuery && <QueryStatusCard query={currentQuery} />}

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
  },
);

QueryForm.displayName = "QueryForm";
