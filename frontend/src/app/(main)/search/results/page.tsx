'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowLeft, Search, Globe, Database, Network, FileText } from 'lucide-react';
import { StreamingSearch } from '@/components/search/StreamingSearch';
import { motion } from 'framer-motion';

export default function SearchResultsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'All' | 'Web' | 'Vector' | 'KG' | 'Comprehensive'>('All');

  useEffect(() => {
    const q = searchParams.get('q');
    const m = searchParams.get('mode') as any;
    if (q) setQuery(q);
    if (m) setMode(m);
  }, [searchParams]);

  const searchModes = [
    { id: 'All', label: 'All', icon: Search, description: 'Search across all sources' },
    { id: 'Web', label: 'Web', icon: Globe, description: 'Web search and real-time data' },
    { id: 'Vector', label: 'Vector', icon: Database, description: 'Vector database search' },
    { id: 'KG', label: 'KG', icon: Network, description: 'Knowledge graph traversal' },
    { id: 'Comprehensive', label: 'Comprehensive', icon: FileText, description: 'Deep analysis with citations' }
  ];

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-4 mb-8"
        >
          <button
            onClick={() => router.back()}
            className="cosmic-btn-ghost p-2"
            aria-label="Go back"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold cosmic-text-primary">Search Results</h1>
            <p className="cosmic-text-secondary">Query: "{query}"</p>
            </div>
        </motion.div>

        {/* Search Mode Pills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-2 mb-8"
        >
          {searchModes.map((searchMode) => (
            <button
              key={searchMode.id}
              onClick={() => setMode(searchMode.id as any)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                mode === searchMode.id
                  ? 'cosmic-btn-primary'
                  : 'cosmic-btn-secondary'
              }`}
              title={searchMode.description}
            >
              <searchMode.icon className="w-4 h-4" />
              {searchMode.label}
            </button>
          ))}
        </motion.div>

        {/* Search Interface */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="cosmic-card p-6"
        >
          <StreamingSearch
            onComplete={(data) => {
              console.log('Search completed:', data);
            }}
            onError={(error) => {
              console.error('Search error:', error);
            }}
            className="w-full"
          />
        </motion.div>
      </div>
    </div>
  );
}
