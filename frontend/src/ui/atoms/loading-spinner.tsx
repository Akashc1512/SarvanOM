import React from "react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  color?: "primary" | "secondary" | "white" | "blue" | "green";
  className?: string;
  "aria-label"?: string;
  variant?: "spinner" | "dots" | "pulse";
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
  xl: "h-12 w-12",
};

const colorClasses = {
  primary: "text-primary",
  secondary: "text-secondary",
  white: "text-white",
  blue: "text-blue-600",
  green: "text-green-600",
};

export const LoadingSpinner = React.memo<LoadingSpinnerProps>(
  ({
    size = "md",
    color = "primary",
    className,
    "aria-label": ariaLabel = "Loading...",
    variant = "spinner",
  }) => {
    if (variant === "dots") {
      return (
        <div
          className={cn("flex space-x-1", className)}
          role="status"
          aria-label={ariaLabel}
        >
          <div className={cn("animate-bounce", sizeClasses[size], colorClasses[color])}>
            <div className="w-full h-full rounded-full bg-current" />
          </div>
          <div className={cn("animate-bounce", sizeClasses[size], colorClasses[color])} style={{ animationDelay: "0.1s" }}>
            <div className="w-full h-full rounded-full bg-current" />
          </div>
          <div className={cn("animate-bounce", sizeClasses[size], colorClasses[color])} style={{ animationDelay: "0.2s" }}>
            <div className="w-full h-full rounded-full bg-current" />
          </div>
          <span className="sr-only">{ariaLabel}</span>
        </div>
      );
    }

    if (variant === "pulse") {
      return (
        <div
          className={cn(
            "animate-pulse rounded-full bg-current",
            sizeClasses[size],
            colorClasses[color],
            className,
          )}
          role="status"
          aria-label={ariaLabel}
        >
          <span className="sr-only">{ariaLabel}</span>
        </div>
      );
    }

    return (
      <div
        className={cn(
          "inline-block animate-spin rounded-full border-2 border-current border-t-transparent",
          sizeClasses[size],
          colorClasses[color],
          className,
        )}
        role="status"
        aria-label={ariaLabel}
      >
        <span className="sr-only">{ariaLabel}</span>
      </div>
    );
  },
);

LoadingSpinner.displayName = "LoadingSpinner";
