import React from "react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  color?: "primary" | "secondary" | "white";
  className?: string;
  "aria-label"?: string;
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
};

export const LoadingSpinner = React.memo<LoadingSpinnerProps>(
  ({
    size = "md",
    color = "primary",
    className,
    "aria-label": ariaLabel = "Loading...",
  }) => {
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
