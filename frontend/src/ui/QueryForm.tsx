'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MagnifyingGlassIcon as SearchIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

interface QueryFormProps {
  onSubmit?: (query: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  loading?: boolean;
}

export default function QueryForm({
  onSubmit,
  placeholder = "Ask anything...",
  className,
  disabled = false,
  loading = false
}: QueryFormProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled && !loading) {
      onSubmit?.(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className={cn('w-full', className)}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 cosmic-text-tertiary" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          disabled={disabled || loading}
          className="cosmic-input w-full pl-12 pr-4 py-3 text-lg"
        />
        <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
          <motion.button
            type="submit"
            disabled={!query.trim() || disabled || loading}
            className={cn(
              'cosmic-btn-primary px-4 py-2 text-sm font-medium',
              (!query.trim() || disabled || loading) && 'opacity-50 cursor-not-allowed'
            )}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {loading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <SparklesIcon className="h-4 w-4" />
              </motion.div>
            ) : (
              'Search'
            )}
          </motion.button>
        </div>
      </div>
    </form>
  );
}