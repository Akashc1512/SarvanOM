"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  RocketLaunchIcon, 
  MagnifyingGlassIcon, 
  ChartBarIcon, 
  UserIcon,
  SparklesIcon,
  ArrowRightIcon,
  CloudArrowUpIcon,
  HomeIcon
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";
import { SearchInput } from "@/components/search/SearchInput";
import { AnswerDisplay } from "@/components/search/AnswerDisplay";
import { CitationsPanel } from "@/components/search/CitationsPanel";
import { UploadModal } from "@/components/upload/UploadModal";
import { apiService, type Citation, type SearchResponse } from "@/lib/api";
import { useSearchSessionStore } from "@/lib/store";

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSearchMode, setIsSearchMode] = useState(false);
  
  // Get state from Zustand store
  const {
    queryText,
    answerContent,
    citations,
    isLoading: isSearching,
    searchError,
    isUploadModalOpen,
    isCitationsExpanded,
    setQueryText,
    setAnswerContent,
    setCitations,
    setLoading,
    setSearchError,
    setUploadModalOpen,
    setCitationsExpanded,
    resetSession,
  } = useSearchSessionStore();

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleSearch = async (query: string) => {
    // Reset and initialize store state
    resetSession();
    setQueryText(query);
    setLoading(true);
    setSearchError("");
    
    try {
      // Call real backend API
      const searchResponse: SearchResponse = await apiService.search({
        query: query,
        user_id: "anonymous", // You can replace this with actual user ID when auth is implemented
        filters: {}
      });
      
      // Extract results and create a comprehensive answer
      const allResults = [
        ...(searchResponse.results || []),
        ...(searchResponse.zero_budget_results || [])
      ];
      
      if (allResults.length > 0) {
        // Create a comprehensive answer from the search results
        const answer = `Based on the latest research and developments, here's what I found about "${query}":

${allResults.slice(0, 3).map((result, index) => 
  `${index + 1}. ${result.title} - ${result.snippet}`
).join('\n\n')}

${allResults.length > 3 ? `\n\nAdditional ${allResults.length - 3} sources were found with relevance scores ranging from ${Math.min(...allResults.map(r => r.relevance_score))} to ${Math.max(...allResults.map(r => r.relevance_score))}.` : ''}

The search was processed in ${searchResponse.processing_time_ms}ms with a confidence score of ${Math.round(searchResponse.confidence_score * 100)}%. ${searchResponse.zero_budget_enabled ? 'Zero-budget retrieval was enabled, providing additional free-tier sources.' : ''}`;
        
        setAnswerContent(answer);
        
        // Convert backend results to citations
        const converted = apiService.convertToCitations(allResults);
        setCitations(converted);
      } else {
        const noResultsMessage = `I searched for "${query}" but couldn't find any relevant results. Please try rephrasing your query or check if the backend services are running.`;
        setAnswerContent(noResultsMessage);
      }
      
    } catch (error) {
      console.error('Search failed:', error);
      const errorMessage = `Search failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please check if the backend is running on http://localhost:8000`;
      setSearchError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (files: File[]) => {
    console.log("Uploading files:", files);
    
    try {
      // Upload each file to the backend
      const uploadPromises = files.map(async (file) => {
        try {
          const result = await apiService.uploadFile(file, {
            filename: file.name,
            size: file.size,
            type: file.type,
            uploaded_at: new Date().toISOString()
          });
          console.log(`File ${file.name} uploaded successfully:`, result);
          return { file, success: true, result };
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          return { file, success: false, error };
        }
      });
      
      const results = await Promise.all(uploadPromises);
      const successful = results.filter(r => r.success);
      const failed = results.filter(r => !r.success);
      
      if (successful.length > 0) {
        console.log(`${successful.length} files uploaded successfully`);
      }
      
      if (failed.length > 0) {
        console.error(`${failed.length} files failed to upload`);
      }
      
    } catch (error) {
      console.error('Upload process failed:', error);
    }
  };

  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-gray-100 dark:bg-slate-950 dark:text-slate-100 cosmic-bg relative overflow-hidden">
        {/* VSCode-Inspired Cosmic Starfield Background */}
        <div className="absolute inset-0 cosmic-starfield opacity-20 dark:hidden"></div>
        <div className="hidden dark:block absolute inset-0 cosmic-starfield-dark opacity-30"></div>
        
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-6"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-20 h-20 mx-auto"
            >
              <RocketLaunchIcon className="w-full h-full text-vscode-accent-purple" />
            </motion.div>
            <div className="space-y-3">
              <h1 className="text-3xl font-bold text-vscode-text-primary">
                SarvanOM
              </h1>
              <p className="text-lg text-vscode-text-secondary max-w-md mx-auto">
                Initializing cosmic knowledge platform...
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // Search mode - Main dashboard interface
  if (isSearchMode) {
    return (
      <div className="min-h-screen bg-black text-gray-100 dark:bg-slate-950 dark:text-slate-100 cosmic-bg relative overflow-hidden">
        {/* VSCode-Inspired Cosmic Starfield Background */}
        <div className="absolute inset-0 cosmic-starfield opacity-20 dark:hidden"></div>
        <div className="hidden dark:block absolute inset-0 cosmic-starfield-dark opacity-30"></div>
        
        <div className="relative z-10">
          {/* Header with Navigation and Upload Button */}
          <header className="border-b border-vscode-border/20 bg-cosmos-bg-vscode/50 backdrop-blur-sm">
            <div className="max-w-screen-xl mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setIsSearchMode(false)}
                    className="p-2 rounded-lg hover:bg-white/10 dark:hover:bg-gray-800/50 transition-colors text-white dark:text-gray-100"
                    aria-label="Return to home"
                  >
                    <HomeIcon className="w-6 h-6" />
                  </button>
                  <div>
                    <h1 className="text-2xl font-bold text-vscode-text-primary">Knowledge Search</h1>
                    <p className="text-vscode-text-secondary">Ask questions and discover insights</p>
                  </div>
                </div>
                
                <button
                  onClick={() => setUploadModalOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-vscode-accent-purple hover:bg-vscode-accent-blue text-white rounded-lg transition-all shadow-lg hover:shadow-xl cosmic-glow-purple"
                  aria-label="Upload files"
                >
                  <CloudArrowUpIcon className="w-5 h-5" />
                  <span>Upload Files</span>
                </button>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="max-w-screen-xl mx-auto p-4 space-y-6">
            {/* Search Input */}
            <section aria-label="Search Interface">
              <SearchInput
                onSearch={handleSearch}
                isLoading={isSearching}
                placeholder="Ask anything about knowledge, research, or insights..."
              />
            </section>

            {/* Results Area - Responsive Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Answer Display - Takes 2/3 of the space on large screens */}
              <section className="lg:col-span-2" aria-label="AI Answer Section">
                <AnswerDisplay
                  answer={answerContent}
                  isLoading={isSearching}
                  error={searchError}
                  confidence={0.95}
                  processingTime={3.2}
                  citations={citations}
                  traceId={searchError ? undefined : `trace_${Date.now()}`}
                />
              </section>

              {/* Citations Panel - Takes 1/3 of the space on large screens */}
              <aside className="lg:col-span-1" role="complementary" aria-label="Sources">
                <CitationsPanel
                  citations={citations}
                  isExpanded={isCitationsExpanded}
                  onToggle={() => setCitationsExpanded(!isCitationsExpanded)}
                />
              </aside>
            </div>
          </main>
        </div>

        {/* Upload Modal */}
        <UploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
          onUpload={handleUpload}
        />
      </div>
    );
  }

  // Landing page content
  const features = [
    {
      icon: MagnifyingGlassIcon,
      title: "Advanced Search",
      description: "AI-powered knowledge discovery across multiple sources with semantic understanding and real-time results.",
      color: "cosmic-text-blue"
    },
    {
      icon: ChartBarIcon,
      title: "Analytics Dashboard",
      description: "Comprehensive insights and performance metrics with interactive visualizations and trend analysis.",
      color: "cosmic-text-green"
    },
    {
      icon: UserIcon,
      title: "Collaboration Hub",
      description: "Team-based knowledge sharing and management with real-time collaboration features.",
      color: "cosmic-text-purple"
    }
  ];

  return (
    <div className="min-h-screen bg-black text-gray-100 dark:bg-slate-950 dark:text-slate-100 cosmic-bg relative overflow-hidden">
      {/* VSCode-Inspired Cosmic Starfield Background */}
      <div className="absolute inset-0 cosmic-starfield opacity-20 dark:hidden"></div>
      <div className="hidden dark:block absolute inset-0 cosmic-starfield-dark opacity-30"></div>
      
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="relative py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center space-y-12"
            >
              {/* Hero Icon */}
              <div className="relative">
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{ 
                    duration: 4, 
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="w-32 h-32 mx-auto mb-8"
                >
                  <RocketLaunchIcon className="w-full h-full text-vscode-accent-purple" />
                </motion.div>
                <SparklesIcon className="absolute -top-4 -right-4 w-10 h-10 text-vscode-accent-purple/60" />
              </div>
              
              {/* Hero Content */}
              <div className="space-y-8">
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-vscode-text-primary leading-tight">
                  Welcome to{" "}
                  <span className="cosmic-text-gradient">
                    SarvanOM
                  </span>
                </h1>
                
                <p className="text-xl sm:text-2xl text-vscode-text-secondary max-w-3xl mx-auto leading-relaxed">
                  The next-generation universal knowledge platform powered by advanced AI and cosmic intelligence
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsSearchMode(true)}
                    className="group bg-vscode-accent-purple hover:bg-vscode-accent-blue text-white px-8 py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl flex items-center gap-3 cosmic-glow-purple"
                  >
                    Start Exploring
                    <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => router.push('/analytics')}
                    className="border border-vscode-border hover:border-vscode-accent-blue text-vscode-accent-blue px-8 py-4 rounded-xl font-semibold transition-all duration-300 backdrop-blur-sm cosmic-bg-vscode"
                  >
                    View Analytics
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
          <div className="absolute inset-0 cosmic-bg-vscode opacity-50 backdrop-blur-sm"></div>
          <div className="relative z-10 max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-center space-y-16"
            >
              <div className="space-y-6">
                <h2 className="text-4xl sm:text-5xl font-bold text-vscode-text-primary">
                  Platform Features
                </h2>
                <p className="text-xl text-vscode-text-secondary max-w-2xl mx-auto">
                  Discover the powerful capabilities that make SarvanOM the ultimate knowledge platform
                </p>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-12">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.3 + index * 0.1 }}
                    className="group cosmic-bg-vscode rounded-2xl p-8 hover:shadow-xl hover:-translate-y-2 transition-all duration-300 border border-vscode-border hover:border-vscode-accent-blue"
                  >
                    <div className="space-y-6">
                      <div className={cn("w-16 h-16 rounded-xl bg-vscode-accent-purple/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300", feature.color)}>
                        <feature.icon className="w-8 h-8" />
                      </div>
                      
                      <div className="space-y-4">
                        <h3 className="text-2xl font-semibold text-vscode-text-primary">
                          {feature.title}
                        </h3>
                        <p className="text-vscode-text-secondary leading-relaxed">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-y-6"
            >
              <h2 className="text-4xl sm:text-5xl font-bold text-vscode-text-primary">
                Ready to Explore?
              </h2>
              <p className="text-xl text-vscode-text-secondary">
                Join thousands of users discovering knowledge with SarvanOM
              </p>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsSearchMode(true)}
                className="bg-gradient-to-r from-vscode-accent-purple to-vscode-accent-blue hover:from-vscode-accent-blue hover:to-vscode-accent-purple text-white px-10 py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl cosmic-glow-purple"
              >
                Get Started Now
              </motion.button>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
}