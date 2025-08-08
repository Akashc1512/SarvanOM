"use client";

import { Sparkles } from "lucide-react";

interface CosmicLoaderProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
}

export function CosmicLoader({ size = "md", text, className = "" }: CosmicLoaderProps) {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-12 w-12", 
    lg: "h-16 w-16"
  };

  const textSizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className="relative mb-4">
        <Sparkles className={`${sizeClasses[size]} text-purple-600 dark:text-purple-400 animate-pulse`} />
        <div className={`absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-pulse`} />
      </div>
      {text && (
        <p className={`${textSizes[size]} text-gray-600 dark:text-gray-300 text-center`}>
          {text}
        </p>
      )}
      <div className="flex justify-center space-x-2 mt-4">
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100" />
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200" />
      </div>
    </div>
  );
}

export function CosmicSpinner({ size = "md", className = "" }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  return (
    <div className={`animate-spin ${className}`}>
      <svg 
        className={`${sizeClasses[size]} text-purple-600 dark:text-purple-400`}
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          className="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4"
        />
        <path 
          className="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}
