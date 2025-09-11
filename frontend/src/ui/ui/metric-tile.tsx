import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "./card";

const metricTileVariants = cva(
  "cosmic-card p-6 transition-all duration-200 hover:cosmic-card-elevated",
  {
    variants: {
      tone: {
        primary: "border-cosmic-primary-500/20",
        success: "border-cosmic-success/20",
        warning: "border-cosmic-warning/20",
        danger: "border-cosmic-error/20",
        neutral: "border-cosmic-border-primary",
      },
      size: {
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      },
    },
    defaultVariants: {
      tone: "primary",
      size: "md",
    },
  },
);

export interface MetricTileProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof metricTileVariants> {
  label: string;
  value: string | number;
  delta?: string;
  deltaType?: "increase" | "decrease" | "neutral";
  icon?: React.ReactNode;
  description?: string;
  loading?: boolean;
}

const MetricTile = React.forwardRef<HTMLDivElement, MetricTileProps>(
  (
    {
      className,
      tone,
      size,
      label,
      value,
      delta,
      deltaType = "neutral",
      icon,
      description,
      loading = false,
      ...props
    },
    ref,
  ) => {
    const deltaColorMap = {
      increase: "text-cosmic-success",
      decrease: "text-cosmic-error",
      neutral: "text-cosmic-text-tertiary",
    };

    const deltaIconMap = {
      increase: "↗",
      decrease: "↘",
      neutral: "",
    };

    if (loading) {
      return (
        <Card
          ref={ref}
          className={cn(metricTileVariants({ tone, size }), className)}
          {...props}
        >
          <CardContent className="space-y-3">
            <div className="h-4 bg-cosmic-bg-tertiary rounded animate-pulse" />
            <div className="h-8 bg-cosmic-bg-tertiary rounded animate-pulse" />
            <div className="h-4 bg-cosmic-bg-tertiary rounded w-2/3 animate-pulse" />
          </CardContent>
        </Card>
      );
    }

    return (
      <Card
        ref={ref}
        className={cn(metricTileVariants({ tone, size }), className)}
        {...props}
      >
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-xs font-medium cosmic-text-tertiary uppercase tracking-wide">
              {label}
            </div>
            {icon && (
              <div className="cosmic-text-tertiary">
                {icon}
              </div>
            )}
          </div>
          
          <div className="text-3xl font-semibold cosmic-text-primary">
            {value}
          </div>
          
          {delta && (
            <div className={cn(
              "text-sm font-medium flex items-center gap-1",
              deltaColorMap[deltaType]
            )}>
              <span>{deltaIconMap[deltaType]}</span>
              <span>{delta}</span>
            </div>
          )}
          
          {description && (
            <div className="text-sm cosmic-text-tertiary">
              {description}
            </div>
          )}
        </CardContent>
      </Card>
    );
  },
);

MetricTile.displayName = "MetricTile";

export { MetricTile, metricTileVariants };
