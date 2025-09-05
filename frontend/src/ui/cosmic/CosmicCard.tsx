'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CosmicCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'elevated' | 'outlined';
  glow?: boolean;
  hover?: boolean;
  children: React.ReactNode;
}

export const CosmicCard: React.FC<CosmicCardProps> = ({
  variant = 'default',
  glow = false,
  hover = true,
  className,
  children,
  ...props
}) => {
  const variants = {
    default: 'cosmic-card',
    glass: 'cosmic-card-glass',
    elevated: 'cosmic-card shadow-2xl',
    outlined: 'cosmic-card border-2 border-cosmic-border-accent'
  };

  return (
    <motion.div
      className={cn(
        variants[variant],
        glow && 'cosmic-glow-soft',
        hover && 'cosmic-hover-lift',
        className
      )}
      whileHover={hover ? { y: -2 } : undefined}
      transition={{ duration: 0.2 }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

interface CosmicCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CosmicCardHeader: React.FC<CosmicCardHeaderProps> = ({
  className,
  children,
  ...props
}) => (
  <div
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  >
    {children}
  </div>
);

interface CosmicCardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

export const CosmicCardTitle: React.FC<CosmicCardTitleProps> = ({
  className,
  children,
  ...props
}) => (
  <h3
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight cosmic-text-primary',
      className
    )}
    {...props}
  >
    {children}
  </h3>
);

interface CosmicCardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export const CosmicCardDescription: React.FC<CosmicCardDescriptionProps> = ({
  className,
  children,
  ...props
}) => (
  <p
    className={cn('text-sm cosmic-text-secondary', className)}
    {...props}
  >
    {children}
  </p>
);

interface CosmicCardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CosmicCardContent: React.FC<CosmicCardContentProps> = ({
  className,
  children,
  ...props
}) => (
  <div
    className={cn('p-6 pt-0', className)}
    {...props}
  >
    {children}
  </div>
);

interface CosmicCardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CosmicCardFooter: React.FC<CosmicCardFooterProps> = ({
  className,
  children,
  ...props
}) => (
  <div
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  >
    {children}
  </div>
);

export {
  CosmicCard as Card,
  CosmicCardHeader as CardHeader,
  CosmicCardTitle as CardTitle,
  CosmicCardDescription as CardDescription,
  CosmicCardContent as CardContent,
  CosmicCardFooter as CardFooter,
};
