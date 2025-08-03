import React from "react";
import { cn } from "@/lib/utils";

export type StatusType =
  | "success"
  | "error"
  | "warning"
  | "info"
  | "pending"
  | "processing"
  | "completed"
  | "failed";

interface StatusBadgeProps {
  status: StatusType;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const statusConfig = {
  success: {
    className: "bg-green-100 text-green-800 border-green-200",
    icon: "✓",
  },
  error: {
    className: "bg-red-100 text-red-800 border-red-200",
    icon: "✗",
  },
  warning: {
    className: "bg-yellow-100 text-yellow-800 border-yellow-200",
    icon: "⚠",
  },
  info: {
    className: "bg-blue-100 text-blue-800 border-blue-200",
    icon: "ℹ",
  },
  pending: {
    className: "bg-gray-100 text-gray-800 border-gray-200",
    icon: "⏳",
  },
  processing: {
    className: "bg-blue-100 text-blue-800 border-blue-200",
    icon: "⟳",
  },
  completed: {
    className: "bg-green-100 text-green-800 border-green-200",
    icon: "✓",
  },
  failed: {
    className: "bg-red-100 text-red-800 border-red-200",
    icon: "✗",
  },
};

const sizeClasses = {
  sm: "px-2 py-1 text-xs",
  md: "px-3 py-1.5 text-sm",
  lg: "px-4 py-2 text-base",
};

export const StatusBadge = React.memo<StatusBadgeProps>(
  ({ status, size = "md", showIcon = false, className, children }) => {
    const config = statusConfig[status];
    const displayText = children || status;

    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border font-medium",
          config.className,
          sizeClasses[size],
          className,
        )}
        role="status"
        aria-label={`Status: ${status}`}
      >
        {showIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {config.icon}
          </span>
        )}
        <span className="capitalize">{displayText}</span>
      </span>
    );
  },
);

StatusBadge.displayName = "StatusBadge";
