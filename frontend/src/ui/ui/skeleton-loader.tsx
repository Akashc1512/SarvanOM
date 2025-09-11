"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface SkeletonLoaderProps {
  className?: string;
  variant?: 'default' | 'card' | 'text' | 'avatar' | 'button' | 'image';
  lines?: number;
  width?: string | number;
  height?: string | number;
  animate?: boolean;
}

export function SkeletonLoader({
  className,
  variant = 'default',
  lines = 1,
  width,
  height,
  animate = true
}: SkeletonLoaderProps) {
  const baseClasses = "cosmic-bg-secondary rounded animate-pulse";
  
  const variants = {
    default: "h-4 w-full",
    card: "h-48 w-full rounded-lg",
    text: "h-4 w-full",
    avatar: "h-10 w-10 rounded-full",
    button: "h-10 w-24 rounded-md",
    image: "h-64 w-full rounded-lg"
  };

  const skeletonClasses = cn(
    baseClasses,
    variants[variant],
    className
  );

  const skeletonStyle = {
    width: width || undefined,
    height: height || undefined,
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            className={cn(
              skeletonClasses,
              index === lines - 1 ? "w-3/4" : "w-full"
            )}
            style={skeletonStyle}
            initial={animate ? { opacity: 0.5 } : { opacity: 1 }}
            animate={animate ? { opacity: [0.5, 1, 0.5] } : { opacity: 1 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.1
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      className={skeletonClasses}
      style={skeletonStyle}
      initial={animate ? { opacity: 0.5 } : { opacity: 1 }}
      animate={animate ? { opacity: [0.5, 1, 0.5] } : { opacity: 1 }}
      transition={{
        duration: 1.5,
        repeat: Infinity
      }}
    />
  );
}

// Specialized skeleton components
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("cosmic-card p-6 space-y-4", className)}>
      <SkeletonLoader variant="avatar" className="h-12 w-12" />
      <div className="space-y-2">
        <SkeletonLoader variant="text" width="75%" />
        <SkeletonLoader variant="text" width="50%" />
      </div>
      <SkeletonLoader variant="button" />
    </div>
  );
}

export function BlogPostSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("cosmic-card p-6 space-y-4", className)}>
      <SkeletonLoader variant="image" className="h-48 w-full" />
      <div className="space-y-3">
        <SkeletonLoader variant="text" width="90%" />
        <SkeletonLoader variant="text" width="70%" />
        <SkeletonLoader variant="text" width="60%" />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <SkeletonLoader variant="avatar" className="h-8 w-8" />
          <SkeletonLoader variant="text" width="100px" />
        </div>
        <SkeletonLoader variant="button" width="80px" />
      </div>
    </div>
  );
}

export function SearchResultSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("cosmic-card p-6 space-y-4", className)}>
      <div className="space-y-2">
        <SkeletonLoader variant="text" width="85%" />
        <SkeletonLoader variant="text" width="95%" />
        <SkeletonLoader variant="text" width="70%" />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <SkeletonLoader variant="button" width="60px" />
          <SkeletonLoader variant="button" width="80px" />
        </div>
        <SkeletonLoader variant="text" width="120px" />
      </div>
    </div>
  );
}

export function AnalyticsSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="cosmic-card p-6 space-y-3">
            <SkeletonLoader variant="text" width="60%" />
            <SkeletonLoader variant="text" width="40px" height="32px" />
            <SkeletonLoader variant="text" width="80px" />
          </div>
        ))}
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="cosmic-card p-6 space-y-4">
          <SkeletonLoader variant="text" width="200px" />
          <SkeletonLoader variant="card" className="h-64" />
        </div>
        <div className="cosmic-card p-6 space-y-4">
          <SkeletonLoader variant="text" width="180px" />
          <SkeletonLoader variant="card" className="h-64" />
        </div>
      </div>
    </div>
  );
}

export function GraphSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("cosmic-card p-6 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <SkeletonLoader variant="text" width="200px" />
        <div className="flex space-x-2">
          <SkeletonLoader variant="button" width="80px" />
          <SkeletonLoader variant="button" width="80px" />
        </div>
      </div>
      <SkeletonLoader variant="card" className="h-96" />
      <div className="flex items-center justify-between">
        <div className="flex space-x-4">
          <SkeletonLoader variant="text" width="100px" />
          <SkeletonLoader variant="text" width="120px" />
        </div>
        <SkeletonLoader variant="button" width="100px" />
      </div>
    </div>
  );
}

export function UploadSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("cosmic-card p-6 space-y-4", className)}>
      <SkeletonLoader variant="text" width="250px" />
      <SkeletonLoader variant="card" className="h-48" />
      <div className="space-y-2">
        <SkeletonLoader variant="text" width="90%" />
        <SkeletonLoader variant="text" width="70%" />
      </div>
      <SkeletonLoader variant="button" width="120px" />
    </div>
  );
}
