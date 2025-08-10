"use client";

import React, { useState, useEffect } from "react";
import { Loader2, Sparkles, Zap, Brain } from "lucide-react";
import { cn } from "@/lib/utils";

interface StreamingLoaderProps {
  isStreaming: boolean;
  hasStarted: boolean;
  firstTokenReceived: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function StreamingLoader({
  isStreaming,
  hasStarted,
  firstTokenReceived,
  className,
  size = "md"
}: StreamingLoaderProps) {
  const [dots, setDots] = useState("");

  useEffect(() => {
    if (!isStreaming) {
      setDots("");
      return;
    }

    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? "" : prev + ".");
    }, 500);

    return () => clearInterval(interval);
  }, [isStreaming]);

  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6", 
    lg: "h-8 w-8"
  };

  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  };

  if (!isStreaming && !hasStarted) {
    return null;
  }

  return (
    <div className={cn("flex flex-col items-center space-y-3", className)}>
      {/* Animated Icons */}
      <div className="flex items-center space-x-2">
        {!firstTokenReceived && (
          <>
            <Loader2 className={cn(sizeClasses[size], "animate-spin text-purple-600")} />
            <Sparkles className={cn(sizeClasses[size], "animate-pulse text-blue-500")} />
            <Brain className={cn(sizeClasses[size], "animate-bounce text-purple-500")} />
          </>
        )}
        {firstTokenReceived && (
          <Zap className={cn(sizeClasses[size], "animate-pulse text-green-500")} />
        )}
      </div>

      {/* Status Text */}
      <div className={cn("text-center", textSizeClasses[size])}>
        {!hasStarted && (
          <p className="text-gray-600 dark:text-gray-300">
            Preparing your query...
          </p>
        )}
        {hasStarted && !firstTokenReceived && (
          <p className="text-gray-600 dark:text-gray-300">
            AI is thinking{dots}
            <br />
            <span className="text-sm text-gray-500">
              Waiting for first response token...
            </span>
          </p>
        )}
        {firstTokenReceived && isStreaming && (
          <p className="text-green-600 dark:text-green-400">
            Streaming response...
            <br />
            <span className="text-sm text-gray-500">
              Tokens are flowing in real-time
            </span>
          </p>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="w-48 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={cn(
            "h-full transition-all duration-500",
            !firstTokenReceived 
              ? "w-1/3 bg-purple-500 animate-pulse" 
              : "w-full bg-green-500"
          )}
        />
      </div>

      {/* Performance hint */}
      {!firstTokenReceived && hasStarted && (
        <p className="text-xs text-gray-500 max-w-xs text-center">
          Target: First token in &lt;2 seconds for optimal experience
        </p>
      )}
    </div>
  );
}

export default StreamingLoader;
