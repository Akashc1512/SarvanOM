"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Textarea } from "@/ui/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/ui/ui/dialog";
import { 
  Copy, 
  Share2, 
  ThumbsUp, 
  ThumbsDown, 
  MessageSquare, 
  Bookmark,
  Check,
  X,
  Star,
  Clock,
  User,
  TrendingUp,
  AlertCircle,
  Loader2,
  RefreshCw
} from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { api, type QueryResponse } from "@/services/api";
import { CitationPanel } from "./CitationPanel";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { AnswerSkeleton } from "@/ui/atoms/skeleton";
import { LoadingSpinner } from "@/ui/atoms/loading-spinner";
import { QueryErrorBoundary } from "./ErrorBoundary";

interface AnswerDisplayProps {
  query: QueryResponse;
  onFeedback?: (_rating: number, _helpful: boolean, _feedback?: string) => void;
  isLoading?: boolean;
}

export function AnswerDisplay({
  query,
  onFeedback,
  isLoading = false,
}: AnswerDisplayProps) {
  const { toast } = useToast();
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [isSavingToMemory, setIsSavingToMemory] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client side
  useState(() => {
    setIsClient(true);
  });

  const handleCopyAnswer = async () => {
    try {
      if (isClient && navigator.clipboard) {
        await navigator.clipboard.writeText(query.answer || "");
        toast({
          title: "Copied",
          description: "Answer copied to clipboard",
        });
      }
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy answer to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleShare = async () => {
    try {
      const shareData = {
        title: "Research Answer",
        text: query.answer || "",
        url: isClient && typeof window !== "undefined" ? window.location.href : "",
      };

      if (isClient && navigator.share) {
        await navigator.share(shareData);
      } else if (isClient && navigator.clipboard) {
        await navigator.clipboard.writeText(shareData.text);
        toast({
          title: "Shared",
          description: "Answer copied to clipboard for sharing",
        });
      }
    } catch (error) {
      toast({
        title: "Share failed",
        description: "Failed to share the answer",
        variant: "destructive",
      });
    }
  };

  const handleSaveToMemory = async () => {
    if (!query.answer) return;

    setIsSavingToMemory(true);
    try {
      const response = await fetch('/api/memory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_id: query.query_id,
          answer: query.answer,
          query_text: query.query_type || "research",
        }),
      });

      if (response.ok) {
        toast({
          title: "Saved to Memory",
          description: "Answer has been saved to your memory",
        });
      } else {
        throw new Error('Failed to save to memory');
      }
    } catch (error) {
      toast({
        title: "Save Failed",
        description: "Failed to save answer to memory",
        variant: "destructive",
      });
    } finally {
      setIsSavingToMemory(false);
    }
  };

  const handleFeedback = async (rating: number, helpful: boolean) => {
    if (!query.query_id) return;

    setIsSubmittingFeedback(true);
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_id: query.query_id,
          rating,
          helpful,
          feedback: feedbackText,
        }),
      });

      if (response.ok) {
        toast({
          title: "Feedback Submitted",
          description: "Thank you for your feedback!",
        });
        setShowFeedbackForm(false);
        setFeedbackText("");
        onFeedback?.(rating, helpful, feedbackText);
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (error) {
      toast({
        title: "Feedback Failed",
        description: "Failed to submit feedback. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "bg-green-100 text-green-800";
    if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  // Show loading skeleton when loading
  if (isLoading) {
    return (
      <QueryErrorBoundary>
        <Card className="w-full">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <LoadingSpinner size="sm" variant="dots" />
                <span className="text-sm text-muted-foreground">
                  Processing your query...
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <AnswerSkeleton />
          </CardContent>
        </Card>
      </QueryErrorBoundary>
    );
  }

  // Show error state if query failed (check if answer is empty and confidence is low)
  if (!query.answer && query.confidence < 0.3) {
    return (
      <QueryErrorBoundary>
        <Card className="w-full border-destructive/50">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <CardTitle className="text-destructive">Query Failed</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              We encountered an error while processing your query. Please try again.
            </p>
            <Button onClick={() => window.location.reload()} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry Query
            </Button>
          </CardContent>
        </Card>
      </QueryErrorBoundary>
    );
  }

  return (
    <QueryErrorBoundary>
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-primary" />
              <div>
                <CardTitle className="text-lg">AI Response</CardTitle>
                <CardDescription>
                  {query.processing_time && `Processed in ${query.processing_time}ms`}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {query.confidence && (
                <ConfidenceBadge confidence={query.confidence} />
              )}
              {query.query_type === "cached" && (
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                  <Check className="mr-1 h-3 w-3" />
                  Cached
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {query.answer ? (
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {query.answer}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center space-x-2 text-muted-foreground">
                <LoadingSpinner size="sm" variant="dots" />
                <span>Generating answer...</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2 pt-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyAnswer}
              disabled={!query.answer}
            >
              <Copy className="mr-2 h-4 w-4" />
              Copy
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
              disabled={!query.answer}
            >
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSaveToMemory}
              disabled={!query.answer || isSavingToMemory}
            >
              {isSavingToMemory ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Bookmark className="mr-2 h-4 w-4" />
              )}
              {isSavingToMemory ? "Saving..." : "Save"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFeedbackForm(true)}
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              Feedback
            </Button>
          </div>

          {/* Feedback Dialog */}
          <Dialog open={showFeedbackForm} onOpenChange={setShowFeedbackForm}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Provide Feedback</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">Rating:</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <Button
                        key={rating}
                        variant="outline"
                        size="sm"
                        onClick={() => handleFeedback(rating, true)}
                        disabled={isSubmittingFeedback}
                      >
                        <Star className="h-4 w-4" />
                        {rating}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Additional Feedback:</label>
                  <Textarea
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    placeholder="Share your thoughts about this answer..."
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowFeedbackForm(false)}
                    disabled={isSubmittingFeedback}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleFeedback(5, true)}
                    disabled={isSubmittingFeedback}
                  >
                    {isSubmittingFeedback ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Check className="mr-2 h-4 w-4" />
                    )}
                    Submit Feedback
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </QueryErrorBoundary>
  );
}
