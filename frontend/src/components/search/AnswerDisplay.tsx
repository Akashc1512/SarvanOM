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

interface AnswerDisplayProps {
  answer?: string;
  isLoading?: boolean;
  error?: string;
  confidence?: number;
  processingTime?: number;
  className?: string;
}

export function AnswerDisplay({ 
  answer, 
  isLoading, 
  error, 
  confidence = 0.95,
  processingTime,
  className 
}: AnswerDisplayProps) {
  const storeAnswer = useSearchSessionStore((s) => s.answerContent);
  const storeLoading = useSearchSessionStore((s) => s.isLoading);
  const effectiveAnswer = answer ?? storeAnswer;
  const effectiveIsLoading = isLoading ?? storeLoading;
  if (effectiveIsLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("w-full", className)}
      >
        <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-cosmos-accent/20 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-cosmos-accent animate-pulse" />
            </div>
            <div className="flex-1">
              <div className="h-4 bg-cosmos-accent/20 rounded animate-pulse mb-2"></div>
              <div className="h-3 bg-cosmos-accent/10 rounded animate-pulse w-1/2"></div>
            </div>
          </div>
          
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-cosmos-accent/20 rounded animate-pulse"></div>
                <div className="h-4 bg-cosmos-accent/10 rounded animate-pulse w-3/4"></div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex items-center gap-4 text-sm text-cosmos-fg/60">
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
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 bg-red-500/20 rounded-xl flex items-center justify-center">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-red-400">Error Processing Query</h3>
              <p className="text-red-300 text-sm">Something went wrong while processing your request</p>
            </div>
          </div>
          
          <div className="bg-red-500/5 border border-red-500/10 rounded-lg p-4">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
          
          <div className="mt-4">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-all"
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
        <div className="bg-cosmos-card/30 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl p-6 text-center">
          <div className="w-16 h-16 bg-cosmos-accent/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <DocumentTextIcon className="w-8 h-8 text-cosmos-accent" />
          </div>
          <h3 className="text-xl font-semibold text-cosmos-fg mb-2">Ready to Search</h3>
          <p className="text-cosmos-fg/70">
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
      <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-cosmos-accent/20 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-cosmos-accent" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-cosmos-fg">AI Response</h3>
              <div className="flex items-center gap-4 text-sm text-cosmos-fg/60">
                <div className="flex items-center gap-1">
                  <CheckCircleIcon className="w-4 h-4 text-green-400" />
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
            className="text-cosmos-fg leading-relaxed space-y-4"
            aria-live="polite"
            aria-label="AI generated answer"
          >
            {effectiveAnswer.split('\n').map((paragraph, index) => (
              <p key={index} className="text-base text-cosmos-fg/90">
                {paragraph}
              </p>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-8 pt-6 border-t border-cosmos-accent/20 flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-cosmos-fg/60">
            <button className="flex items-center gap-2 hover:text-cosmos-accent transition-colors">
              <LinkIcon className="w-4 h-4" />
              <span>Copy Link</span>
            </button>
            <button className="flex items-center gap-2 hover:text-cosmos-accent transition-colors">
              <DocumentTextIcon className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <button className="px-4 py-2 bg-cosmos-accent/10 hover:bg-cosmos-accent/20 text-cosmos-accent rounded-lg transition-all">
              Follow Up
            </button>
            <button className="px-4 py-2 bg-cosmos-accent hover:bg-cosmos-accent/90 text-cosmos-bg rounded-lg transition-all">
              Ask More
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
