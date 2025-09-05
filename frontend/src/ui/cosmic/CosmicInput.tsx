'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface CosmicInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  label?: string;
  description?: string;
  required?: boolean;
  variant?: 'default' | 'glass' | 'outlined';
  glow?: boolean;
}

const CosmicInput = React.forwardRef<HTMLInputElement, CosmicInputProps>(
  (
    {
      className,
      type,
      error,
      leftIcon,
      rightIcon,
      label,
      description,
      required,
      variant = 'default',
      glow = false,
      id,
      ...props
    },
    ref,
  ) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;

    const variants = {
      default: 'cosmic-input',
      glass: 'cosmic-input bg-cosmic-bg-glass/50 backdrop-blur-sm',
      outlined: 'cosmic-input border-2 border-cosmic-border-accent'
    };

    return (
      <div className="w-full">
        {label && (
          <motion.label
            htmlFor={inputId}
            className="block text-sm font-medium cosmic-text-primary mb-2"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {label}
            {required && <span className="text-cosmic-error ml-1">*</span>}
          </motion.label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 cosmic-text-tertiary">
              {leftIcon}
            </div>
          )}
          <motion.input
            type={type}
            className={cn(
              variants[variant],
              glow && 'cosmic-glow-soft',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-cosmic-error focus:border-cosmic-error focus:ring-cosmic-error/20',
              className,
            )}
            ref={ref}
            id={inputId}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error
                ? `${inputId}-error`
                : description
                  ? `${inputId}-description`
                  : undefined
            }
            whileFocus={{ scale: 1.01 }}
            transition={{ duration: 0.2 }}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 cosmic-text-tertiary">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <motion.p
            id={`${inputId}-error`}
            className="mt-1 text-sm text-cosmic-error"
            role="alert"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {error}
          </motion.p>
        )}
        {description && !error && (
          <motion.p
            id={`${inputId}-description`}
            className="mt-1 text-sm cosmic-text-tertiary"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {description}
          </motion.p>
        )}
      </div>
    );
  },
);

CosmicInput.displayName = 'CosmicInput';

export { CosmicInput };
