"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

import { api, type QueryResponse, type Source } from "@/lib/api";
import {
  ExternalLink,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Share2,
  MessageSquare,
  Calendar,
  Globe,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface AnswerDisplayProps {
  query: QueryResponse;
  onFeedback?: (_rating: number, _helpful: boolean, _feedback?: string) => void;
}

export function AnswerDisplay({
  query,
  onFeedback,
}: AnswerDisplayProps) {
  const { toast } = useToast();
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  const handleCopyAnswer = async () => {
    try {
      await navigator.clipboard.writeText(query.answer || "");
      toast({
        title: "Copied to clipboard",
        description: "The answer has been copied to your clipboard",
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleShare = async () => {
    try {
      const shareData = {
        title: "Research Answer",
        text: query.answer || "",
        url: window.location.href,
      };

      if (navigator.share) {
        await navigator.share(shareData);
      } else {
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

  const handleFeedback = async (rating: number, helpful: boolean) => {
    if (!query.query_id) return;

    setIsSubmittingFeedback(true);
    try {
      await api.submitFeedback({
        query_id: query.query_id,
        rating,
        feedback_text: feedbackText,
        helpful,
      });

      toast({
        title: "Feedback submitted",
        description: "Thank you for your feedback!",
      });

      onFeedback?.(rating, helpful, feedbackText);
      setShowFeedbackForm(false);
      setFeedbackText("");
    } catch (error: any) {
      toast({
        title: "Feedback failed",
        description:
          error.response?.data?.detail || "Failed to submit feedback",
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

  if (!query.answer) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-gray-500">
            <p>
              No answer available yet. Please wait for the query to complete.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Answer */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>AI Research Answer</CardTitle>
              {query.confidence && (
                <Badge className={getConfidenceColor(query.confidence)}>
                  {(query.confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleCopyAnswer}>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button variant="outline" size="sm" onClick={handleShare}>
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
          <CardDescription>
            Generated on {formatDate(query.created_at)}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose prose-gray max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {query.answer}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sources */}
      {query.sources && query.sources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Sources & Citations
            </CardTitle>
            <CardDescription>
              {query.sources.length} source
              {query.sources.length !== 1 ? "s" : ""} used in this research
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {query.sources.map((source: Source, index: number) => (
                <div
                  key={index}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-2">
                        {source.title}
                      </h4>
                      <p className="text-sm text-gray-600 mb-3">
                        {source.snippet}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Relevance: {(source.relevance_score * 100).toFixed(0)}
                          %
                        </span>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(source.url, "_blank")}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Visit
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feedback Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Feedback
          </CardTitle>
          <CardDescription>
            Help us improve by providing feedback on this answer
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => handleFeedback(5, true)}
                disabled={isSubmittingFeedback}
                className="flex-1"
              >
                <ThumbsUp className="h-4 w-4 mr-2" />
                Helpful
              </Button>
              <Button
                variant="outline"
                onClick={() => handleFeedback(1, false)}
                disabled={isSubmittingFeedback}
                className="flex-1"
              >
                <ThumbsDown className="h-4 w-4 mr-2" />
                Not Helpful
              </Button>
            </div>

            {showFeedbackForm && (
              <div className="space-y-3">
                <textarea
                  placeholder="Additional feedback (optional)..."
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                />
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowFeedbackForm(false)}
                    variant="outline"
                    size="sm"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleFeedback(3, true)}
                    disabled={isSubmittingFeedback}
                    size="sm"
                  >
                    Submit Feedback
                  </Button>
                </div>
              </div>
            )}

            {!showFeedbackForm && (
              <Button
                variant="ghost"
                onClick={() => setShowFeedbackForm(true)}
                className="text-sm"
              >
                Add detailed feedback
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Query Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Query Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium text-gray-700">Query ID:</p>
              <p className="text-gray-900 font-mono">{query.query_id}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Status:</p>
              <p className="text-gray-900 capitalize">{query.status}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Created:</p>
              <p className="text-gray-900">{formatDate(query.created_at)}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Updated:</p>
              <p className="text-gray-900">{formatDate(query.updated_at)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
