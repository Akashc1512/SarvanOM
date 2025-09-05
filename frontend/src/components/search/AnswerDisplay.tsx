"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  ClockIcon,
  SparklesIcon,
  DocumentTextIcon,
  LinkIcon
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";
import { useSearchSessionStore } from "@/lib/store";
import { CitationNumber, CitationLink } from "./CitationTooltip";
import { ShareButton } from "./ShareButton";
import type { Citation } from "@/lib/api";

interface AnswerDisplayProps {
  answer?: string;
  isLoading?: boolean;
  error?: string;
  confidence?: number;
  processingTime?: number;
  citations?: Citation[];
  traceId?: string;
  className?: string;
}

export function AnswerDisplay({ 
  answer, 
  isLoading, 
  error, 
  confidence = 0.95,
  processingTime,
  citations = [],
  traceId,
  className 
}: AnswerDisplayProps) {
  const storeAnswer = useSearchSessionStore((s) => s.answerContent);
  const storeLoading = useSearchSessionStore((s) => s.isLoading);
  const storeQuery = useSearchSessionStore((s) => s.queryText);
  const storeCitations = useSearchSessionStore((s) => s.citations);
  
  const effectiveAnswer = answer ?? storeAnswer;
  const effectiveIsLoading = isLoading ?? storeLoading;
  const effectiveCitations = citations.length > 0 ? citations : storeCitations;
  const effectiveQuery = storeQuery;

  // Parse citations from answer text and render with tooltips
  const parseAnswerWithCitations = (text: string) => {
    if (!text || effectiveCitations.length === 0) {
      return text.split('\n').map((paragraph, index) => (
        <p key={index} className="text-base cosmic-text-primary">
          {paragraph}
        </p>
      ));
    }

    // Split by paragraphs and process each one
    return text.split('\n').map((paragraph, paragraphIndex) => {
      // Look for citation patterns like [1], [2], etc.
      const citationPattern = /\[(\d+)\]/g;
      const parts = [];
      let lastIndex = 0;
      let match;

      while ((match = citationPattern.exec(paragraph)) !== null) {
        // Add text before citation
        if (match.index > lastIndex) {
          parts.push(paragraph.slice(lastIndex, match.index));
        }

        // Add citation
        const citationNumber = parseInt(match[1] || '0');
        const citation = effectiveCitations[citationNumber - 1];
        
        if (citation) {
          parts.push(
            <CitationNumber
              key={`${paragraphIndex}-${match.index}`}
              citation={citation}
              number={citationNumber}
            />
          );
        } else {
          // Fallback if citation not found
          parts.push(
            <span
              key={`${paragraphIndex}-${match.index}`}
              className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium bg-muted text-muted-foreground border border-muted-foreground/30 rounded-full"
            >
              {citationNumber}
            </span>
          );
        }

        lastIndex = match.index + match[0].length;
      }

      // Add remaining text
      if (lastIndex < paragraph.length) {
        parts.push(paragraph.slice(lastIndex));
      }

      return (
        <p key={paragraphIndex} className="text-base cosmic-text-primary leading-relaxed">
          {parts}
        </p>
      );
    });
  };
  if (effectiveIsLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("w-full", className)}
      >
        <div className="cosmic-card p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-cosmic-primary-500/20 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-cosmic-primary-500 animate-pulse" />
            </div>
            <div className="flex-1">
              <div className="h-4 bg-cosmic-primary-500/20 rounded animate-pulse mb-2"></div>
              <div className="h-3 bg-cosmic-primary-500/10 rounded animate-pulse w-1/2"></div>
            </div>
          </div>
          
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-cosmic-primary-500/20 rounded animate-pulse"></div>
                <div className="h-4 bg-cosmic-primary-500/10 rounded animate-pulse w-3/4"></div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex items-center gap-4 text-sm cosmic-text-tertiary">
            <div className="flex items-center gap-2">
              <ClockIcon className="w-4 h-4" />
              <span>Processing your query...</span>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("w-full", className)}
      >
        <div className="cosmic-card border-cosmic-error bg-cosmic-error/5 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 bg-cosmic-error/20 rounded-xl flex items-center justify-center">
              <ExclamationTriangleIcon className="w-6 h-6 text-cosmic-error" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-cosmic-error">Error Processing Query</h3>
              <p className="text-cosmic-error/80 text-sm">Something went wrong while processing your request</p>
            </div>
          </div>
          
          <div className="bg-cosmic-error/5 border border-cosmic-error/10 rounded-lg p-4">
            <p className="text-cosmic-error/80 text-sm">{error}</p>
          </div>
          
          <div className="mt-4">
            <button 
              onClick={() => window.location.reload()}
              className="cosmic-btn-secondary bg-cosmic-error/20 hover:bg-cosmic-error/30 text-cosmic-error"
            >
              Try Again
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  if (!effectiveAnswer) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("w-full", className)}
      >
        <div className="cosmic-card p-6 text-center">
          <div className="w-16 h-16 bg-cosmic-primary-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <DocumentTextIcon className="w-8 h-8 text-cosmic-primary-500" />
          </div>
          <h3 className="text-xl font-semibold cosmic-text-primary mb-2">Ready to Search</h3>
          <p className="cosmic-text-secondary">
            Enter your question above to get AI-powered insights and knowledge
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("w-full", className)}
    >
      <div className="cosmic-card p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-cosmic-primary-500/20 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-cosmic-primary-500" />
            </div>
            <div>
              <h3 className="text-xl font-semibold cosmic-text-primary">AI Response</h3>
              <div className="flex items-center gap-4 text-sm cosmic-text-tertiary">
                <div className="flex items-center gap-1">
                  <CheckCircleIcon className="w-4 h-4 text-cosmic-success" />
                  <span>Confidence: {Math.round(confidence * 100)}%</span>
                </div>
                {processingTime && (
                  <div className="flex items-center gap-1">
                    <ClockIcon className="w-4 h-4" />
                    <span>{processingTime.toFixed(1)}s</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Answer Content */}
        <div className="prose prose-invert max-w-none">
          <div 
            className="cosmic-text-primary leading-relaxed space-y-4"
            aria-live="polite"
            aria-label="AI generated answer"
          >
            {parseAnswerWithCitations(effectiveAnswer)}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-8 pt-6 border-t border-cosmic-border-primary flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm cosmic-text-tertiary">
            <button className="cosmic-nav-item flex items-center gap-2">
              <DocumentTextIcon className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
          
          <div className="flex items-center gap-3">
            <ShareButton
              query={effectiveQuery}
              answer={effectiveAnswer}
              citations={effectiveCitations}
              {...(traceId && { traceId })}
              variant="minimal"
              size="sm"
            />
            <button className="cosmic-btn-secondary">
              Follow Up
            </button>
            <button className="cosmic-btn-primary">
              Ask More
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
