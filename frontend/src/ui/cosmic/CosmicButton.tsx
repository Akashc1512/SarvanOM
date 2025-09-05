'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cosmicButtonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cosmic-primary-500 focus-visible:ring-opacity-20 disabled:pointer-events-none disabled:opacity-50 cosmic-hover-lift',
  {
    variants: {
      variant: {
        primary: 'cosmic-btn-primary',
        secondary: 'cosmic-btn-secondary',
        ghost: 'cosmic-btn-ghost',
        outline: 'cosmic-btn-secondary border border-cosmic-border-primary',
        success: 'bg-cosmic-success text-white hover:bg-cosmic-success/90 cosmic-glow-soft',
        warning: 'bg-cosmic-warning text-white hover:bg-cosmic-warning/90 cosmic-glow-soft',
        error: 'bg-cosmic-error text-white hover:bg-cosmic-error/90 cosmic-glow-soft',
        info: 'bg-cosmic-info text-white hover:bg-cosmic-info/90 cosmic-glow-soft',
        link: 'text-cosmic-primary-500 underline-offset-4 hover:underline hover:text-cosmic-primary-400',
        glass: 'cosmic-card-glass border border-cosmic-border-primary hover:bg-cosmic-bg-secondary/50',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        default: 'h-10 px-4 py-2',
        lg: 'h-11 px-8 text-base',
        xl: 'h-12 px-10 text-lg',
        icon: 'h-10 w-10',
        'icon-sm': 'h-8 w-8',
        'icon-lg': 'h-12 w-12',
      },
      glow: {
        true: 'cosmic-glow-primary',
        false: '',
      },
      loading: {
        true: 'relative text-transparent transition-none hover:text-transparent',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
      glow: false,
      loading: false,
    },
  },
);

export interface CosmicButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof cosmicButtonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  pulse?: boolean;
}

const CosmicButton = React.forwardRef<HTMLButtonElement, CosmicButtonProps>(
  (
    {
      className,
      variant,
      size,
      glow,
      loading = false,
      asChild = false,
      leftIcon,
      rightIcon,
      pulse = false,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading;

    const buttonContent = (
      <>
        {loading && (
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <motion.div
              className="h-4 w-4 border-2 border-current border-t-transparent rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
          </div>
        )}
        {!loading && leftIcon && (
          <span className="mr-2 flex items-center">{leftIcon}</span>
        )}
        {children}
        {!loading && rightIcon && (
          <span className="ml-2 flex items-center">{rightIcon}</span>
        )}
        {pulse && !loading && (
          <motion.div
            className="absolute inset-0 rounded-lg bg-cosmic-primary-500/20"
            animate={{ scale: [1, 1.05, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}
      </>
    );

    return (
      <motion.button
        className={cn(cosmicButtonVariants({ variant, size, glow, loading }), className)}
        ref={ref}
        disabled={isDisabled}
        whileHover={!isDisabled ? { scale: 1.02 } : undefined}
        whileTap={!isDisabled ? { scale: 0.98 } : undefined}
        transition={{ duration: 0.1 }}
        {...props}
      >
        {buttonContent}
      </motion.button>
    );
  },
);

CosmicButton.displayName = 'CosmicButton';

export { CosmicButton, cosmicButtonVariants };
