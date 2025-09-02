"use client";

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShareIcon, 
  CheckIcon, 
  LinkIcon,
  ClipboardDocumentIcon 
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import type { Citation } from '@/lib/api';

interface ShareButtonProps {
  query: string;
  answer: string;
  citations: Citation[];
  traceId?: string;
  className?: string;
  variant?: 'default' | 'minimal' | 'icon-only';
  size?: 'sm' | 'md' | 'lg';
}

interface ShareData {
  query: string;
  answer: string;
  citations: Citation[];
  traceId?: string;
  timestamp: number;
  expiresAt: number;
}

export function ShareButton({ 
  query, 
  answer, 
  citations, 
  traceId,
  className = "",
  variant = 'default',
  size = 'md'
}: ShareButtonProps) {
  const [isCopied, setIsCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate shareable permalink
  const generatePermalink = useCallback(async (): Promise<string> => {
    try {
      setIsLoading(true);
      setError(null);

      // Create share data with 24-hour expiration
      const shareData: ShareData = {
        query,
        answer,
        citations,
        traceId,
        timestamp: Date.now(),
        expiresAt: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      };

      // Encode the data
      const encodedData = btoa(JSON.stringify(shareData));
      
      // Create permalink
      const baseUrl = window.location.origin;
      const permalink = `${baseUrl}/shared/${encodedData}`;
      
      return permalink;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate permalink';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [query, answer, citations, traceId]);

  // Copy to clipboard
  const copyToClipboard = useCallback(async (text: string) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      return true;
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      return false;
    }
  }, []);

  // Handle share action
  const handleShare = useCallback(async () => {
    try {
      const permalink = await generatePermalink();
      const success = await copyToClipboard(permalink);
      
      if (success) {
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
      } else {
        setError('Failed to copy to clipboard');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to share');
    }
  }, [generatePermalink, copyToClipboard]);

  // Handle native share API (if available)
  const handleNativeShare = useCallback(async () => {
    try {
      if (navigator.share) {
        const permalink = await generatePermalink();
        await navigator.share({
          title: `SarvanOM Search: ${query}`,
          text: `Check out this search result: ${query}`,
          url: permalink
        });
        return;
      }
      
      // Fallback to copy to clipboard
      await handleShare();
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        // User cancelled, fallback to copy
        await handleShare();
      }
    }
  }, [generatePermalink, handleShare, query]);

  // Get size classes
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-sm';
      case 'lg':
        return 'px-6 py-3 text-lg';
      default:
        return 'px-4 py-2 text-base';
    }
  };

  // Get icon size
  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'lg':
        return 'w-6 h-6';
      default:
        return 'w-5 h-5';
    }
  };

  // Render different variants
  if (variant === 'icon-only') {
    return (
      <motion.button
        onClick={handleNativeShare}
        disabled={isLoading}
        className={cn(
          "inline-flex items-center justify-center rounded-lg",
          "bg-primary/10 hover:bg-primary/20 text-primary",
          "border border-primary/20 hover:border-primary/30",
          "transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          size === 'sm' ? 'w-8 h-8' : size === 'lg' ? 'w-12 h-12' : 'w-10 h-10',
          className
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Share this search result"
      >
        <AnimatePresence mode="wait">
          {isCopied ? (
            <motion.div
              key="check"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
            >
              <CheckIcon className={getIconSize()} />
            </motion.div>
          ) : (
            <motion.div
              key="share"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
            >
              {isLoading ? (
                <ClipboardDocumentIcon className={cn(getIconSize(), "animate-pulse")} />
              ) : (
                <ShareIcon className={getIconSize()} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    );
  }

  if (variant === 'minimal') {
    return (
      <motion.button
        onClick={handleNativeShare}
        disabled={isLoading}
        className={cn(
          "inline-flex items-center gap-2 rounded-lg",
          "bg-transparent hover:bg-primary/10 text-primary",
          "border border-primary/20 hover:border-primary/30",
          "transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          getSizeClasses(),
          className
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        aria-label="Share this search result"
      >
        <AnimatePresence mode="wait">
          {isCopied ? (
            <motion.div
              key="check"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-2"
            >
              <CheckIcon className={getIconSize()} />
              <span>Copied!</span>
            </motion.div>
          ) : (
            <motion.div
              key="share"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <ClipboardDocumentIcon className={cn(getIconSize(), "animate-pulse")} />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <ShareIcon className={getIconSize()} />
                  <span>Share</span>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    );
  }

  // Default variant
  return (
    <div className={cn("relative", className)}>
      <motion.button
        onClick={handleNativeShare}
        disabled={isLoading}
        className={cn(
          "inline-flex items-center gap-3 rounded-lg font-medium",
          "bg-primary hover:bg-primary/90 text-primary-foreground",
          "border border-primary/20 hover:border-primary/30",
          "transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "shadow-sm hover:shadow-md",
          getSizeClasses(),
          className
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        aria-label="Share this search result"
      >
        <AnimatePresence mode="wait">
          {isCopied ? (
            <motion.div
              key="check"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-2"
            >
              <CheckIcon className={getIconSize()} />
              <span>Link Copied!</span>
            </motion.div>
          ) : (
            <motion.div
              key="share"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <ClipboardDocumentIcon className={cn(getIconSize(), "animate-pulse")} />
                  <span>Generating Link...</span>
                </>
              ) : (
                <>
                  <ShareIcon className={getIconSize()} />
                  <span>Share Result</span>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 mt-2 px-3 py-2 bg-destructive text-destructive-foreground text-sm rounded-md shadow-lg z-10"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Hook for managing shared content
export function useSharedContent() {
  const [sharedData, setSharedData] = useState<ShareData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSharedContent = useCallback(async (encodedData: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const decodedData = atob(encodedData);
      const data: ShareData = JSON.parse(decodedData);

      // Check if the shared content has expired
      if (data.expiresAt && Date.now() > data.expiresAt) {
        throw new Error('This shared link has expired (24 hours)');
      }

      setSharedData(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load shared content';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    sharedData,
    isLoading,
    error,
    loadSharedContent
  };
}
