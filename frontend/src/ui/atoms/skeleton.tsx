import React from "react";
import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "title" | "paragraph" | "card" | "avatar" | "button" | "chart" | "list";
  lines?: number;
  height?: string;
  width?: string;
}

export const Skeleton = React.memo<SkeletonProps>(
  ({ 
    className, 
    variant = "text", 
    lines = 1, 
    height, 
    width 
  }) => {
    const baseClasses = "animate-pulse bg-gray-200 rounded";

    if (variant === "title") {
      return (
        <div
          className={cn(
            baseClasses,
            "h-8 w-3/4",
            className
          )}
          style={{ height, width }}
        />
      );
    }

    if (variant === "paragraph") {
      return (
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, i) => (
            <div
              key={i}
              className={cn(
                baseClasses,
                "h-4",
                i === lines - 1 ? "w-2/3" : "w-full",
                className
              )}
              style={{ height, width }}
            />
          ))}
        </div>
      );
    }

    if (variant === "card") {
      return (
        <div className={cn("p-6 border rounded-lg", className)}>
          <div className={cn(baseClasses, "h-6 w-1/3 mb-4")} />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className={cn(
                  baseClasses,
                  "h-4",
                  i === 2 ? "w-1/2" : "w-full"
                )}
              />
            ))}
          </div>
        </div>
      );
    }

    if (variant === "avatar") {
      return (
        <div
          className={cn(
            baseClasses,
            "rounded-full",
            height || "h-10",
            width || "w-10",
            className
          )}
        />
      );
    }

    if (variant === "button") {
      return (
        <div
          className={cn(
            baseClasses,
            "h-10 w-24 rounded-md",
            className
          )}
          style={{ height, width }}
        />
      );
    }

    if (variant === "chart") {
      return (
        <div className={cn("space-y-4", className)}>
          <div className={cn(baseClasses, "h-6 w-1/3")} />
          <div className={cn(baseClasses, "h-64 w-full rounded-lg")} />
        </div>
      );
    }

    if (variant === "list") {
      return (
        <div className="space-y-3">
          {Array.from({ length: lines }).map((_, i) => (
            <div
              key={i}
              className={cn(
                baseClasses,
                "h-4",
                i === lines - 1 ? "w-2/3" : "w-full"
              )}
            />
          ))}
        </div>
      );
    }

    // Default text variant
    return (
      <div
        className={cn(
          baseClasses,
          "h-4 w-full",
          className
        )}
        style={{ height, width }}
      />
    );
  }
);

Skeleton.displayName = "Skeleton";

// Specialized skeleton components
export const AnswerSkeleton = () => (
  <div className="space-y-4">
    <div className="flex items-center space-x-2">
      <Skeleton variant="avatar" height="h-8" width="w-8" />
      <div className="space-y-2 flex-1">
        <Skeleton variant="title" />
        <Skeleton variant="paragraph" lines={2} />
      </div>
    </div>
    <div className="space-y-3">
      <Skeleton variant="paragraph" lines={3} />
      <Skeleton variant="paragraph" lines={2} />
    </div>
  </div>
);

export const AnalyticsSkeleton = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} variant="card" />
      ))}
    </div>
    <Skeleton variant="chart" />
  </div>
);

export const CitationSkeleton = () => (
  <div className="space-y-4">
    {Array.from({ length: 3 }).map((_, i) => (
      <div key={i} className="border rounded-lg p-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <Skeleton variant="title" />
            <Skeleton variant="paragraph" lines={2} />
            <div className="flex space-x-2">
              <Skeleton variant="button" />
              <Skeleton variant="button" />
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
); 