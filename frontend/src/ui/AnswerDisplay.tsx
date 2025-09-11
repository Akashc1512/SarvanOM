"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Copy, 
  ThumbsUp, 
  ThumbsDown,
  ExternalLink 
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnswerDisplayProps {
  answer?: string;
  isLoading?: boolean;
  error?: string | null;
  confidence?: number;
  processingTime?: number;
  citations?: any[];
  traceId?: string;
  className?: string;
}

export default function AnswerDisplay({
  answer,
  isLoading = false,
  error = null,
  confidence = 0,
  processingTime = 0,
  citations = [],
  traceId,
  className
}: AnswerDisplayProps) {
  if (isLoading) {
    return (
      <Card className={cn("cosmic-card", className)}>
        <CardHeader>
          <CardTitle className="cosmic-text-primary flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-cosmic-primary-500 border-t-transparent"></div>
            Generating Answer...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="h-4 cosmic-bg-secondary rounded animate-pulse"></div>
            <div className="h-4 cosmic-bg-secondary rounded animate-pulse w-3/4"></div>
            <div className="h-4 cosmic-bg-secondary rounded animate-pulse w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("cosmic-card border-cosmic-error", className)}>
        <CardHeader>
          <CardTitle className="cosmic-text-primary flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-cosmic-error" />
            Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="cosmic-text-secondary mb-4">{error}</p>
          {traceId && (
            <div className="flex items-center gap-2 text-sm cosmic-text-tertiary">
              <span>Trace ID: {traceId}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigator.clipboard.writeText(traceId)}
                className="h-6 px-2"
              >
                <Copy className="h-3 w-3" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  if (!answer) {
    return (
      <Card className={cn("cosmic-card", className)}>
        <CardHeader>
          <CardTitle className="cosmic-text-primary">AI Answer</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="cosmic-text-secondary text-center py-8">
            Enter a query to get started with AI-powered research and analysis.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className={cn("cosmic-card", className)}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="cosmic-text-primary">AI Answer</CardTitle>
            <div className="flex items-center gap-2">
              {confidence > 0 && (
                <Badge variant="outline" className="border-cosmic-success text-cosmic-success">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {Math.round(confidence * 100)}% confidence
                </Badge>
              )}
              {processingTime > 0 && (
                <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                  <Clock className="h-3 w-3 mr-1" />
                  {processingTime}s
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none cosmic-text-primary">
            <div 
              className="whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: answer }}
            />
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-cosmic-border-primary">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="cosmic-btn-secondary">
                <ThumbsUp className="h-4 w-4 mr-1" />
                Helpful
              </Button>
              <Button variant="ghost" size="sm" className="cosmic-btn-secondary">
                <ThumbsDown className="h-4 w-4 mr-1" />
                Not Helpful
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigator.clipboard.writeText(answer)}
                className="cosmic-btn-secondary"
              >
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </Button>
              {citations.length > 0 && (
                <Button variant="ghost" size="sm" className="cosmic-btn-secondary">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  View Sources ({citations.length})
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}