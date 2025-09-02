"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLinkIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import type { Citation } from '@/lib/api';

interface CitationTooltipProps {
  citation: Citation;
  children: React.ReactNode;
  className?: string;
  delay?: number;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export function CitationTooltip({ 
  citation, 
  children, 
  className = "",
  delay = 100,
  position = 'top'
}: CitationTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const handleMouseEnter = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    const id = setTimeout(() => {
      setIsVisible(true);
    }, delay);
    setTimeoutId(id);
  };

  const handleMouseLeave = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    setIsVisible(false);
  };

  const handleFocus = () => {
    setIsVisible(true);
  };

  const handleBlur = () => {
    setIsVisible(false);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    const cleanup = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
    return cleanup;
  }, [timeoutId]);

  // Check for reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Get position classes based on position prop
  const getPositionClasses = () => {
    switch (position) {
      case 'top':
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
      case 'bottom':
        return 'top-full left-1/2 transform -translate-x-1/2 mt-2';
      case 'left':
        return 'right-full top-1/2 transform -translate-y-1/2 mr-2';
      case 'right':
        return 'left-full top-1/2 transform -translate-y-1/2 ml-2';
      default:
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
    }
  };

  // Get arrow classes based on position
  const getArrowClasses = () => {
    switch (position) {
      case 'top':
        return 'top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-popover';
      case 'bottom':
        return 'bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-popover';
      case 'left':
        return 'left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-l-4 border-transparent border-l-popover';
      case 'right':
        return 'right-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-popover';
      default:
        return 'top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-popover';
    }
  };

  return (
    <div 
      ref={triggerRef}
      className={cn("relative inline-block", className)}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleFocus}
      onBlur={handleBlur}
      tabIndex={0}
      role="button"
      aria-label={`Citation ${citation.id}: ${citation.title}`}
      aria-describedby={`citation-tooltip-${citation.id}`}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            id={`citation-tooltip-${citation.id}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ 
              duration: prefersReducedMotion ? 0 : 0.15,
              ease: "easeOut"
            }}
            className={cn(
              "absolute z-50 px-4 py-3 bg-popover text-popover-foreground text-sm rounded-lg shadow-lg border border-border max-w-xs",
              getPositionClasses()
            )}
            role="tooltip"
            aria-live="polite"
          >
            {/* Citation Header */}
            <div className="flex items-start gap-2 mb-2">
              <DocumentTextIcon className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-foreground line-clamp-2 leading-tight">
                  {citation.title}
                </h4>
                {citation.author && (
                  <p className="text-xs text-muted-foreground mt-1">
                    by {citation.author}
                  </p>
                )}
              </div>
            </div>

            {/* Citation Excerpt */}
            {citation.excerpt && (
              <div className="mb-3">
                <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                  {citation.excerpt}
                </p>
              </div>
            )}

            {/* Citation Metadata */}
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 bg-muted rounded text-xs font-medium">
                  {citation.type}
                </span>
                {citation.relevance && (
                  <span>
                    {Math.round(citation.relevance * 100)}% relevant
                  </span>
                )}
              </div>
              
              {citation.url && (
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-primary hover:text-primary/80 transition-colors"
                  aria-label={`Open ${citation.title} in new tab`}
                >
                  <ExternalLinkIcon className="w-3 h-3" />
                  <span>View</span>
                </a>
              )}
            </div>

            {/* Arrow */}
            <div className={cn("absolute", getArrowClasses())} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Enhanced citation number component with tooltip
interface CitationNumberProps {
  citation: Citation;
  number: number;
  className?: string;
}

export function CitationNumber({ citation, number, className = "" }: CitationNumberProps) {
  return (
    <CitationTooltip citation={citation} delay={50}>
      <span 
        className={cn(
          "inline-flex items-center justify-center w-5 h-5 text-xs font-medium",
          "bg-primary/20 text-primary border border-primary/30 rounded-full",
          "hover:bg-primary/30 hover:border-primary/50 transition-all duration-150",
          "cursor-help focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
          "select-none",
          className
        )}
        aria-label={`Citation ${number}: ${citation.title}`}
      >
        {number}
      </span>
    </CitationTooltip>
  );
}

// Citation link component for inline citations
interface CitationLinkProps {
  citation: Citation;
  number: number;
  className?: string;
}

export function CitationLink({ citation, number, className = "" }: CitationLinkProps) {
  return (
    <CitationTooltip citation={citation} delay={50}>
      <a
        href={citation.url || '#'}
        target={citation.url ? "_blank" : undefined}
        rel={citation.url ? "noopener noreferrer" : undefined}
        className={cn(
          "inline-flex items-center justify-center w-5 h-5 text-xs font-medium",
          "bg-primary/20 text-primary border border-primary/30 rounded-full",
          "hover:bg-primary/30 hover:border-primary/50 transition-all duration-150",
          "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
          "select-none no-underline",
          !citation.url && "cursor-help",
          className
        )}
        aria-label={`Citation ${number}: ${citation.title}`}
        onClick={!citation.url ? (e) => e.preventDefault() : undefined}
      >
        {number}
      </a>
    </CitationTooltip>
  );
}
