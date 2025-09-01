"use client";

import React from "react";
import { motion } from "framer-motion";

interface StandardLayoutProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

export function StandardLayout({ 
  children, 
  className = "", 
  title,
  description 
}: StandardLayoutProps) {
  return (
    <div className={`min-h-screen cosmic ${className}`}>
      <div className="container-std">
        {(title || description) && (
          <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="section-std"
          >
            {title && (
              <h1 className="text-title text-[var(--fg)] mb-4">
                {title}
              </h1>
            )}
            {description && (
              <p className="text-body text-[var(--fg)]/80 max-w-3xl">
                {description}
              </p>
            )}
          </motion.header>
        )}
        
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="section-std"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}

interface StandardCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

export function StandardCard({ 
  children, 
  className = "", 
  title,
  description 
}: StandardCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className={`card-std p-6 ${className}`}
    >
      {title && (
        <h3 className="text-xl font-semibold text-[var(--fg)] mb-3">
          {title}
        </h3>
      )}
      {description && (
        <p className="text-body text-[var(--fg)]/70 mb-4">
          {description}
        </p>
      )}
      {children}
    </motion.div>
  );
}

interface StandardButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "outline";
  size?: "sm" | "md" | "lg";
  className?: string;
  disabled?: boolean;
}

export function StandardButton({ 
  children, 
  onClick,
  variant = "primary",
  size = "md",
  className = "",
  disabled = false
}: StandardButtonProps) {
  const baseClasses = "font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variantClasses = {
    primary: "bg-[var(--accent)] text-white hover:opacity-90 focus:ring-[var(--accent)]",
    secondary: "bg-[var(--card)] text-[var(--fg)] border border-white/20 hover:border-white/40 focus:ring-white/20",
    outline: "border border-[var(--accent)] text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white focus:ring-[var(--accent)]"
  };
  
  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };
  
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className} ${
        disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
      }`}
    >
      {children}
    </motion.button>
  );
}
