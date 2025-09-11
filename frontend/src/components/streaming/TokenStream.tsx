"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TokenStreamProps {
  text: string;
  isStreaming?: boolean;
  speed?: number; // tokens per second
  className?: string;
  onComplete?: () => void;
  showCursor?: boolean;
  cursorBlinkSpeed?: number;
}

export function TokenStream({
  text,
  isStreaming = false,
  speed = 20, // 20 tokens per second default
  className,
  onComplete,
  showCursor = true,
  cursorBlinkSpeed = 500
}: TokenStreamProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const cursorRef = useRef<HTMLSpanElement>(null);

  // Reset when text changes
  useEffect(() => {
    if (text !== displayedText) {
      setDisplayedText('');
      setCurrentIndex(0);
      setIsComplete(false);
    }
  }, [text, displayedText]);

  // Handle streaming animation
  useEffect(() => {
    if (!isStreaming || currentIndex >= text.length) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      
      if (currentIndex >= text.length && !isComplete) {
        setIsComplete(true);
        onComplete?.();
      }
      return;
    }

    const interval = 1000 / speed; // Convert tokens per second to milliseconds per token
    
    intervalRef.current = setInterval(() => {
      setCurrentIndex(prev => {
        const nextIndex = prev + 1;
        if (nextIndex <= text.length) {
          setDisplayedText(text.slice(0, nextIndex));
          return nextIndex;
        }
        return prev;
      });
    }, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isStreaming, currentIndex, text.length, speed, isComplete, onComplete, text]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Cursor blinking animation
  useEffect(() => {
    if (!showCursor || !cursorRef.current) return;

    const cursor = cursorRef.current;
    const blinkInterval = setInterval(() => {
      cursor.style.opacity = cursor.style.opacity === '0' ? '1' : '0';
    }, cursorBlinkSpeed);

    return () => clearInterval(blinkInterval);
  }, [showCursor, cursorBlinkSpeed]);

  return (
    <div className={cn('cosmic-text-primary', className)}>
      <span className="whitespace-pre-wrap">
        {displayedText}
        {showCursor && isStreaming && (
          <motion.span
            ref={cursorRef}
            className="inline-block w-0.5 h-5 bg-cosmic-primary-500 ml-1"
            initial={{ opacity: 1 }}
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: cursorBlinkSpeed / 1000, repeat: Infinity }}
          />
        )}
      </span>
      
      {/* Streaming indicator */}
      <AnimatePresence>
        {isStreaming && !isComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="inline-flex items-center ml-2"
          >
            <motion.div
              className="w-2 h-2 bg-cosmic-primary-500 rounded-full"
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5]
              }}
              transition={{ 
                duration: 1,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface HeartbeatBarProps {
  isActive: boolean;
  lastHeartbeat?: number;
  className?: string;
  showPulse?: boolean;
}

export function HeartbeatBar({
  isActive,
  lastHeartbeat,
  className,
  showPulse = true
}: HeartbeatBarProps) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (isActive && showPulse) {
      const interval = setInterval(() => {
        setPulse(true);
        setTimeout(() => setPulse(false), 200);
      }, 2000); // Pulse every 2 seconds

      return () => clearInterval(interval);
    }
  }, [isActive, showPulse]);

  const getLastHeartbeatText = () => {
    if (!lastHeartbeat) return '';
    const elapsed = Date.now() - lastHeartbeat;
    if (elapsed < 1000) return 'Just now';
    if (elapsed < 60000) return `${Math.floor(elapsed / 1000)}s ago`;
    return `${Math.floor(elapsed / 60000)}m ago`;
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex items-center gap-2">
        <div className="relative">
          <div className={cn(
            'w-3 h-3 rounded-full transition-colors duration-200',
            isActive ? 'bg-cosmic-success' : 'bg-cosmic-text-tertiary'
          )} />
          {isActive && showPulse && (
            <motion.div
              className="absolute inset-0 w-3 h-3 rounded-full bg-cosmic-success"
              animate={{ 
                scale: pulse ? [1, 1.5, 1] : 1,
                opacity: pulse ? [0.5, 0, 0.5] : 0.5
              }}
              transition={{ duration: 0.6 }}
            />
          )}
        </div>
        <span className={cn(
          'text-xs font-medium',
          isActive ? 'text-cosmic-success' : 'text-cosmic-text-tertiary'
        )}>
          {isActive ? 'Live' : 'Offline'}
        </span>
      </div>
      
      {lastHeartbeat && (
        <span className="text-xs cosmic-text-tertiary">
          {getLastHeartbeatText()}
        </span>
      )}
    </div>
  );
}

interface StreamingProgressProps {
  progress: number; // 0-100
  isStreaming?: boolean;
  className?: string;
  showPercentage?: boolean;
}

export function StreamingProgress({
  progress,
  isStreaming = false,
  className,
  showPercentage = true
}: StreamingProgressProps) {
  return (
    <div className={cn('w-full', className)}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm cosmic-text-secondary">Progress</span>
        {showPercentage && (
          <span className="text-sm cosmic-text-secondary">
            {Math.round(progress)}%
          </span>
        )}
      </div>
      
      <div className="w-full bg-cosmic-bg-secondary rounded-full h-2 overflow-hidden">
        <motion.div
          className={cn(
            'h-full rounded-full transition-colors duration-200',
            isStreaming ? 'bg-cosmic-primary-500' : 'bg-cosmic-success'
          )}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
        
        {isStreaming && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{ x: ['-100%', '100%'] }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              ease: 'linear'
            }}
          />
        )}
      </div>
    </div>
  );
}

interface StreamingStatsProps {
  tokensPerSecond?: number;
  totalTokens?: number;
  elapsedTime?: number;
  className?: string;
}

export function StreamingStats({
  tokensPerSecond,
  totalTokens,
  elapsedTime,
  className
}: StreamingStatsProps) {
  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  return (
    <div className={cn('flex items-center gap-4 text-xs cosmic-text-tertiary', className)}>
      {tokensPerSecond && (
        <div className="flex items-center gap-1">
          <span>⚡</span>
          <span>{tokensPerSecond.toFixed(1)} tok/s</span>
        </div>
      )}
      
      {totalTokens && (
        <div className="flex items-center gap-1">
          <span>📝</span>
          <span>{totalTokens} tokens</span>
        </div>
      )}
      
      {elapsedTime && (
        <div className="flex items-center gap-1">
          <span>⏱️</span>
          <span>{formatTime(elapsedTime)}</span>
        </div>
      )}
    </div>
  );
}
