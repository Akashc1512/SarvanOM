'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cosmicBadgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-cosmic-primary-500 text-white hover:bg-cosmic-primary-600',
        secondary: 'border-transparent bg-cosmic-secondary-500 text-white hover:bg-cosmic-secondary-600',
        success: 'border-transparent bg-cosmic-success text-white hover:bg-cosmic-success/90',
        warning: 'border-transparent bg-cosmic-warning text-white hover:bg-cosmic-warning/90',
        error: 'border-transparent bg-cosmic-error text-white hover:bg-cosmic-error/90',
        info: 'border-transparent bg-cosmic-info text-white hover:bg-cosmic-info/90',
        outline: 'border-cosmic-border-primary text-cosmic-text-primary hover:bg-cosmic-bg-secondary',
        ghost: 'border-transparent text-cosmic-text-primary hover:bg-cosmic-bg-secondary',
        glass: 'border-cosmic-border-primary/50 bg-cosmic-bg-glass/50 backdrop-blur-sm text-cosmic-text-primary',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        default: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
      glow: {
        true: 'cosmic-glow-soft',
        false: '',
      },
      pulse: {
        true: 'animate-pulse',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      glow: false,
      pulse: false,
    },
  },
);

export interface CosmicBadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cosmicBadgeVariants> {
  children: React.ReactNode;
  icon?: React.ReactNode;
  removable?: boolean;
  onRemove?: () => void;
}

const CosmicBadge = React.forwardRef<HTMLDivElement, CosmicBadgeProps>(
  (
    {
      className,
      variant,
      size,
      glow,
      pulse,
      children,
      icon,
      removable = false,
      onRemove,
      ...props
    },
    ref,
  ) => {
    return (
      <motion.div
        className={cn(cosmicBadgeVariants({ variant, size, glow, pulse }), className)}
        ref={ref}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        transition={{ duration: 0.2 }}
        {...props}
      >
        {icon && <span className="mr-1 flex items-center">{icon}</span>}
        {children}
        {removable && (
          <button
            onClick={onRemove}
            className="ml-1 inline-flex h-3 w-3 items-center justify-center rounded-full hover:bg-black/20 focus:outline-none focus:ring-1 focus:ring-white/50"
            aria-label="Remove badge"
          >
            <svg
              className="h-2 w-2"
              fill="currentColor"
              viewBox="0 0 8 8"
            >
              <path d="m0 0 1 1 3-3 3 3 1-1-4-4-4 4z" />
            </svg>
          </button>
        )}
      </motion.div>
    );
  },
);

CosmicBadge.displayName = 'CosmicBadge';

export { CosmicBadge, cosmicBadgeVariants };
