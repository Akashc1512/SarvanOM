/**
 * Comprehensive Query Page - SarvanOM v2
 * 
 * Advanced query processing interface with multi-step workflow,
 * progress tracking, and comprehensive result display.
 * Follows Cosmic Pro design system with accessibility features.
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Send, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  FileText,
  Database,
  Globe,
  Newspaper,
  TrendingUp,
  Brain,
  Zap,
  Settings,
  Download,
  Share2,
  Bookmark,
  Eye,
  EyeOff
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { designTokens } from '@/lib/design-tokens';
import GuidedPromptModal from '@/components/GuidedPromptModal';
import { useGuidedPrompt } from '@/hooks/useGuidedPrompt';

interface QueryStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  result?: any;
  error?: string;
  duration?: number;
}

interface ComprehensiveQueryState {
  query: string;
  steps: QueryStep[];
  currentStep: number;
  isRunning: boolean;
  isCompleted: boolean;
  error: string | null;
  totalDuration: number;
  results: {
    web: any[];
    vector: any[];
    knowledge: any[];
    news: any[];
    markets: any[];
    synthesis: any;
  };
}

const defaultSteps: QueryStep[] = [
  {
    id: 'guided-prompt',
    name: 'Guided Prompt Refinement',
    description: 'Analyzing and refining your query for optimal results',
    status: 'pending',
    progress: 0
  },
  {
    id: 'web-search',
    name: 'Web Search',
    description: 'Searching the web for relevant information',
    status: 'pending',
    progress: 0
  },
  {
    id: 'vector-search',
    name: 'Vector Search',
    description: 'Finding semantically similar content in our knowledge base',
    status: 'pending',
    progress: 0
  },
  {
    id: 'knowledge-graph',
    name: 'Knowledge Graph',
    description: 'Exploring connected concepts and relationships',
    status: 'pending',
    progress: 0
  },
  {
    id: 'news-feeds',
    name: 'News & Feeds',
    description: 'Gathering latest news and market information',
    status: 'pending',
    progress: 0
  },
  {
    id: 'synthesis',
    name: 'AI Synthesis',
    description: 'Combining and analyzing all sources to create comprehensive answer',
    status: 'pending',
    progress: 0
  }
];

export default function ComprehensiveQueryPage() {
  const [queryState, setQueryState] = useState<ComprehensiveQueryState>({
    query: '',
    steps: defaultSteps,
    currentStep: 0,
    isRunning: false,
    isCompleted: false,
    error: null,
    totalDuration: 0,
    results: {
      web: [],
      vector: [],
      knowledge: [],
      news: [],
      markets: [],
      synthesis: null
    }
  });

  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [selectedSources, setSelectedSources] = useState({
    web: true,
    vector: true,
    knowledge: true,
    news: true,
    markets: false
  });

  const queryInputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Guided Prompt integration
  const {
    isGuidedPromptEnabled,
    showGuidedPrompt,
    guidedPromptData,
    handleGuidedPromptAccept,
    handleGuidedPromptEdit,
    handleGuidedPromptSkip,
    handleGuidedPromptClose
  } = useGuidedPrompt();

  // Focus input on mount
  useEffect(() => {
    if (queryInputRef.current) {
      queryInputRef.current.focus();
    }
  }, []);

  // Simulate step execution
  const executeStep = async (stepIndex: number): Promise<void> => {
    const step = queryState.steps[stepIndex];
    
    // Update step status to running
    setQueryState(prev => ({
      ...prev,
      steps: prev.steps.map((s, i) => 
        i === stepIndex 
          ? { ...s, status: 'running', progress: 0 }
          : s
      )
    }));

    // Simulate progress
    const startTime = Date.now();
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      
      setQueryState(prev => ({
        ...prev,
        steps: prev.steps.map((s, i) => 
          i === stepIndex 
            ? { ...s, progress }
            : s
        )
      }));
    }

    const duration = Date.now() - startTime;

    // Complete the step
    setQueryState(prev => ({
      ...prev,
      steps: prev.steps.map((s, i) => 
        i === stepIndex 
          ? { ...s, status: 'completed', progress: 100, duration }
          : s
      )
    }));
  };

  // Execute comprehensive query
  const executeComprehensiveQuery = async (query: string) => {
    setQueryState(prev => ({
      ...prev,
      query,
      isRunning: true,
      isCompleted: false,
      error: null,
      currentStep: 0,
      totalDuration: 0
    }));

    const startTime = Date.now();

    try {
      // Execute each step sequentially
      for (let i = 0; i < queryState.steps.length; i++) {
        setQueryState(prev => ({ ...prev, currentStep: i }));
        await executeStep(i);
      }

      const totalDuration = Date.now() - startTime;

      setQueryState(prev => ({
        ...prev,
        isRunning: false,
        isCompleted: true,
        totalDuration
      }));

      // Scroll to results
      if (resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (error) {
      setQueryState(prev => ({
        ...prev,
        isRunning: false,
        error: error instanceof Error ? error.message : 'Query execution failed'
      }));
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (queryState.query.trim()) {
      executeComprehensiveQuery(queryState.query);
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Get step icon
  const getStepIcon = (step: QueryStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  // Get step icon by ID
  const getStepIconById = (stepId: string) => {
    switch (stepId) {
      case 'guided-prompt':
        return <Zap className="w-4 h-4" />;
      case 'web-search':
        return <Globe className="w-4 h-4" />;
      case 'vector-search':
        return <Database className="w-4 h-4" />;
      case 'knowledge-graph':
        return <Brain className="w-4 h-4" />;
      case 'news-feeds':
        return <Newspaper className="w-4 h-4" />;
      case 'synthesis':
        return <FileText className="w-4 h-4" />;
      default:
        return <Search className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Comprehensive Query</h1>
              <p className="text-gray-600">Advanced multi-source information gathering and analysis</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                aria-label="Advanced options"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Query Form */}
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                ref={queryInputRef}
                type="text"
                value={queryState.query}
                onChange={(e) => setQueryState(prev => ({ ...prev, query: e.target.value }))}
                onKeyPress={handleKeyPress}
                placeholder="Ask a comprehensive question... (e.g., 'Analyze the current state of AI in healthcare')"
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                disabled={queryState.isRunning}
                aria-label="Comprehensive query"
              />
              <button
                type="submit"
                disabled={queryState.isRunning || !queryState.query.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Execute comprehensive query"
              >
                {queryState.isRunning ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>

          {/* Advanced Options */}
          <AnimatePresence>
            {showAdvancedOptions && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
              >
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Data Sources</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {Object.entries(selectedSources).map(([source, enabled]) => (
                    <label key={source} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={(e) => setSelectedSources(prev => ({
                          ...prev,
                          [source]: e.target.checked
                        }))}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700 capitalize">{source}</span>
                    </label>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        {queryState.isRunning && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-8"
          >
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Processing Steps</h2>
              <div className="space-y-4">
                {queryState.steps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className={cn(
                      'flex items-center gap-4 p-4 rounded-lg border-2 transition-all duration-200',
                      step.status === 'running' && 'border-blue-200 bg-blue-50',
                      step.status === 'completed' && 'border-green-200 bg-green-50',
                      step.status === 'error' && 'border-red-200 bg-red-50',
                      step.status === 'pending' && 'border-gray-200 bg-white'
                    )}
                  >
                    <div className="flex-shrink-0">
                      {getStepIcon(step)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getStepIconById(step.id)}
                        <h3 className="font-medium text-gray-900">{step.name}</h3>
                        {step.duration && (
                          <span className="text-sm text-gray-500">
                            ({step.duration}ms)
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                      
                      {step.status === 'running' && (
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <motion.div
                            className="bg-blue-600 h-2 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${step.progress}%` }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                      )}
                      
                      {step.error && (
                        <p className="text-sm text-red-600 mt-1">{step.error}</p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {queryState.isCompleted && (
          <motion.div
            ref={resultsRef}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Results Header */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Comprehensive Analysis</h2>
                  <p className="text-gray-600">
                    Completed in {queryState.totalDuration}ms
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    aria-label="Download results"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  <button
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    aria-label="Share results"
                  >
                    <Share2 className="w-4 h-4" />
                    Share
                  </button>
                  <button
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    aria-label="Bookmark results"
                  >
                    <Bookmark className="w-4 h-4" />
                    Save
                  </button>
                </div>
              </div>

              {/* Synthesis Result */}
              {queryState.results.synthesis && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-3">AI Synthesis</h3>
                  <div className="prose prose-blue max-w-none">
                    <p className="text-blue-800 leading-relaxed">
                      {queryState.results.synthesis.content || 'Synthesis result will appear here...'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Source Results */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(queryState.results).filter(([key]) => key !== 'synthesis').map(([source, results]) => (
                <div key={source} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    {getStepIconById(source)}
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {source} Results
                    </h3>
                    <span className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-600">
                      {Array.isArray(results) ? results.length : 0}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {Array.isArray(results) && results.length > 0 ? (
                      results.slice(0, 3).map((result, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-1">
                            {result.title || `Result ${index + 1}`}
                          </h4>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {result.content || result.description || 'No content available'}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No results found</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Error State */}
        {queryState.error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-red-50 border border-red-200 rounded-lg p-6"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="text-lg font-semibold text-red-900">Query Failed</h3>
                <p className="text-red-800">{queryState.error}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!queryState.isRunning && !queryState.isCompleted && !queryState.error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="w-12 h-12 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Comprehensive Analysis
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Get in-depth analysis by searching multiple sources simultaneously. 
              Our AI will synthesize information from web, knowledge base, news, and more.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                'Analyze the current state of renewable energy',
                'Compare different AI approaches in healthcare',
                'Research the impact of remote work on productivity'
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => executeComprehensiveQuery(suggestion)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Guided Prompt Modal */}
      <GuidedPromptModal
        isOpen={showGuidedPrompt}
        originalQuery={guidedPromptData?.originalQuery || ''}
        refinements={guidedPromptData?.refinements || []}
        constraints={guidedPromptData?.constraints || []}
        onAccept={handleGuidedPromptAccept}
        onEdit={handleGuidedPromptEdit}
        onSkip={handleGuidedPromptSkip}
        onClose={handleGuidedPromptClose}
        isLoading={false}
        deviceType="desktop"
        language="en"
      />
    </div>
  );
}