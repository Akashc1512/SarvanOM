"use client";

import { useState } from "react";
import { CheckCircle, XCircle, AlertTriangle, Clock } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";

import { api, type QueryResponse, type Source } from "@/services/api";
import { SourcesList } from "@/ui/SourcesList";
import { CitationPanel } from "@/ui/CitationPanel";
import { ExpertValidationButton } from "@/ui/ExpertValidationButton";
import { parseCitations } from "@/utils/citation-parser";
import {
  ExternalLink,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Share2,
  MessageSquare,
  Calendar,
  Globe,
  Bookmark,
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

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
  const [isSavingToMemory, setIsSavingToMemory] = useState(false);
  const [validationStatus, setValidationStatus] = useState<string | null>(null);
  const [validationConfidence, setValidationConfidence] = useState<number | null>(null);

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
          title: `Research: ${query.query_id}`,
          content: query.answer,
          summary: query.answer.substring(0, 200) + '...',
          tags: ['research', 'ai-answer'],
          category: 'Research',
          source_query: query.query_id,
          confidence: query.confidence || 0.8
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save to memory');
      }

      toast({
        title: "Saved to Memory",
        description: "Your research answer has been saved to your knowledge workspace",
      });
    } catch (error) {
      toast({
        title: "Save failed",
        description: "Failed to save to memory",
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
              {validationStatus && (
                <Badge 
                  variant="outline" 
                  className={`${
                    validationStatus === "supported" ? "bg-green-100 text-green-800 border-green-200" :
                    validationStatus === "contradicted" ? "bg-red-100 text-red-800 border-red-200" :
                    "bg-yellow-100 text-yellow-800 border-yellow-200"
                  }`}
                >
                  {validationStatus === "supported" && <CheckCircle className="h-3 w-3 mr-1" />}
                  {validationStatus === "contradicted" && <XCircle className="h-3 w-3 mr-1" />}
                  {validationStatus === "unclear" && <AlertTriangle className="h-3 w-3 mr-1" />}
                  {validationStatus === "pending" && <Clock className="h-3 w-3 mr-1" />}
                  {validationStatus === "supported" ? "Expert Verified ✅" : 
                   validationStatus === "contradicted" ? "Failed ❌" : 
                   "Validation Pending ⏳"}
                  {validationConfidence && (
                    <span className="ml-1 font-medium">
                      {(validationConfidence * 100).toFixed(0)}%
                    </span>
                  )}
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
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleSaveToMemory}
                disabled={isSavingToMemory}
              >
                <Bookmark className="h-4 w-4 mr-2" />
                {isSavingToMemory ? "Saving..." : "Save to Memory"}
              </Button>
              <ExpertValidationButton 
                claim={query.answer || ""}
                queryId={query.query_id}
                variant="outline"
                size="sm"
                onValidationComplete={(status, confidence) => {
                  setValidationStatus(status);
                  setValidationConfidence(confidence);
                }}
              />
            </div>
          </div>
          <CardDescription>
            Generated on {formatDate(query.created_at)}
            {query.llm_provider && (
              <span className="block mt-1 text-sm text-gray-500">
                Answered by: {query.llm_provider} {query.llm_model && `(${query.llm_model})`}
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose prose-gray max-w-none">
            <div 
              className="whitespace-pre-wrap text-gray-800 leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: parseCitations(query.answer || "", query.sources || []) 
              }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Sources */}
      {query.sources && query.sources.length > 0 && (
        <CitationPanel sources={query.sources} />
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
