"use client";

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  ExclamationTriangleIcon, 
  ClockIcon,
  ArrowLeftIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { AnswerDisplay } from '@/components/search/AnswerDisplay';
import { CitationsPanel } from '@/components/search/CitationsPanel';
import { ShareButton } from '@/components/search/ShareButton';
import { useSharedContent } from '@/components/search/ShareButton';
import { cn } from '@/lib/utils';
import type { Citation } from '@/lib/api';

interface ShareData {
  query: string;
  answer: string;
  citations: Citation[];
  traceId?: string;
  timestamp: number;
  expiresAt: number;
}

export default function SharedContentPage() {
  const params = useParams();
  const router = useRouter();
  const { sharedData, isLoading, error, loadSharedContent } = useSharedContent();
  const [isExpanded, setIsExpanded] = useState(true);

  const encodedData = params.encodedData as string;

  useEffect(() => {
    if (encodedData) {
      loadSharedContent(encodedData).catch(console.error);
    }
  }, [encodedData, loadSharedContent]);

  const handleGoBack = () => {
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-cosmos-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="w-16 h-16 bg-cosmos-accent/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <ShareIcon className="w-8 h-8 text-cosmos-accent animate-pulse" />
            </div>
            <h2 className="text-2xl font-semibold text-cosmos-fg mb-2">Loading Shared Content</h2>
            <p className="text-cosmos-fg/70">Please wait while we load the shared search result...</p>
          </motion.div>
        </div>
      </div>
    );
  }

  if (error || !sharedData) {
    return (
      <div className="min-h-screen bg-cosmos-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="w-16 h-16 bg-red-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-2xl font-semibold text-red-400 mb-2">Unable to Load Shared Content</h2>
            <p className="text-red-300 mb-6">{error || 'The shared link could not be loaded.'}</p>
            <button
              onClick={handleGoBack}
              className="inline-flex items-center gap-2 px-6 py-3 bg-cosmos-accent hover:bg-cosmos-accent/90 text-cosmos-bg rounded-lg transition-all"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Go Back to Search</span>
            </button>
          </motion.div>
        </div>
      </div>
    );
  }

  const isExpired = sharedData.expiresAt && Date.now() > sharedData.expiresAt;
  const timeRemaining = sharedData.expiresAt ? Math.max(0, sharedData.expiresAt - Date.now()) : 0;
  const hoursRemaining = Math.floor(timeRemaining / (1000 * 60 * 60));

  return (
    <div className="min-h-screen bg-cosmos-bg">
      {/* Header */}
      <header className="border-b border-cosmos-accent/20 bg-cosmos-card/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
            <button
              onClick={handleGoBack}
              className="flex items-center gap-2 px-4 py-2 text-cosmos-fg/70 hover:text-cosmos-fg transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 rounded-lg"
              aria-label="Return to main search page"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Back to Search</span>
            </button>
              <div className="h-6 w-px bg-cosmos-accent/20" />
              <div>
                <h1 className="text-lg font-semibold text-cosmos-fg" aria-live="polite">Shared Search Result</h1>
                <p className="text-sm text-cosmos-fg/60" aria-label={`Original query: ${sharedData.query}`}>Query: {sharedData.query}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {isExpired ? (
                <div className="flex items-center gap-2 px-3 py-2 bg-red-500/20 text-red-300 rounded-lg text-sm">
                  <ExclamationTriangleIcon className="w-4 h-4" />
                  <span>Expired</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-500/20 text-green-300 rounded-lg text-sm">
                  <ClockIcon className="w-4 h-4" />
                  <span>Expires in {hoursRemaining}h</span>
                </div>
              )}
              
              <ShareButton
                query={sharedData.query}
                answer={sharedData.answer}
                citations={sharedData.citations}
                traceId={sharedData.traceId}
                variant="minimal"
                size="sm"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Answer Display */}
          <section className="lg:col-span-2" aria-label="Shared AI Answer">
            <AnswerDisplay
              answer={sharedData.answer}
              citations={sharedData.citations}
              traceId={sharedData.traceId}
              confidence={0.95}
              processingTime={3.2}
            />
          </section>

          {/* Citations Panel */}
          <aside className="lg:col-span-1" role="complementary" aria-label="Sources">
            <CitationsPanel
              citations={sharedData.citations}
              isExpanded={isExpanded}
              onToggle={() => setIsExpanded(!isExpanded)}
            />
          </aside>
        </div>

        {/* Footer Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 p-4 bg-cosmos-card/20 border border-cosmos-accent/10 rounded-xl"
        >
          <div className="flex items-center justify-between text-sm text-cosmos-fg/60">
            <div className="flex items-center gap-4">
              <span>Shared on {new Date(sharedData.timestamp).toLocaleDateString()}</span>
              {sharedData.traceId && (
                <span>Trace ID: {sharedData.traceId}</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <ShareIcon className="w-4 h-4" />
              <span>This link expires in 24 hours</span>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
