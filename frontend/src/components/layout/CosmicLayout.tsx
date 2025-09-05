'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CosmicLayoutProps {
  children: React.ReactNode;
  className?: string;
  showStarfield?: boolean;
  variant?: 'default' | 'minimal' | 'fullscreen';
}

export const CosmicLayout: React.FC<CosmicLayoutProps> = ({
  children,
  className,
  showStarfield = true,
  variant = 'default'
}) => {
  const variants = {
    default: 'min-h-screen cosmic-bg-primary',
    minimal: 'min-h-screen cosmic-bg-primary',
    fullscreen: 'h-screen w-screen cosmic-bg-primary overflow-hidden'
  };

  return (
    <div className={cn(
      'relative font-sans antialiased',
      variants[variant],
      className
    )}>
      {/* Cosmic Pro Starfield Background */}
      {showStarfield && (
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-0 cosmic-starfield opacity-20" />
          <motion.div
            className="absolute inset-0"
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{
              duration: 30,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
            style={{
              background: `
                radial-gradient(1px 1px at 20% 30%, rgba(59, 130, 246, 0.4) 0, transparent 40%),
                radial-gradient(1px 1px at 80% 20%, rgba(168, 85, 247, 0.3) 0, transparent 40%),
                radial-gradient(1px 1px at 40% 70%, rgba(59, 130, 246, 0.2) 0, transparent 40%),
                radial-gradient(1px 1px at 90% 90%, rgba(168, 85, 247, 0.3) 0, transparent 40%)
              `,
              backgroundSize: '300px 300px, 400px 400px, 200px 200px, 350px 350px',
            }}
          />
        </div>
      )}

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>

      {/* Cosmic Pro Accent Elements */}
      {variant !== 'minimal' && (
        <>
          <motion.div
            className="absolute top-20 left-20 w-2 h-2 bg-cosmic-primary-500 rounded-full cosmic-glow-primary"
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
            }}
          />
          <motion.div
            className="absolute bottom-20 right-20 w-3 h-3 bg-cosmic-secondary-500 rounded-full cosmic-glow-secondary"
            animate={{
              opacity: [0.5, 1, 0.5],
              scale: [1, 2, 1],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              delay: 1,
            }}
          />
          <motion.div
            className="absolute top-1/2 left-10 w-1 h-1 bg-cosmic-primary-400 rounded-full"
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 2, 1],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              delay: 2,
            }}
          />
        </>
      )}
    </div>
  );
};

export default CosmicLayout;
