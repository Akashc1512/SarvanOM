"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Brain, Globe, Search, Zap, Shield, Database, Network, FileText } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { StarField, NebulaEffect } from "@/ui/CosmicParticles";
import { ThemeSelector } from "@/ui/ThemeSelector";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { MobileOptimizedSearch } from "@/ui/MobileOptimizedSearch";
import { StreamingSearch } from "@/components/search/StreamingSearch";
import { useToast } from "@/hooks/useToast";
import { motion } from "framer-motion";

export default function SearchPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [searchMode, setSearchMode] = useState<'All' | 'Web' | 'Vector' | 'KG' | 'Comprehensive'>('All');
  const [isSearching, setIsSearching] = useState(false);

  const searchModes = [
    { id: 'All', label: 'All', icon: Search, description: 'Search across all sources' },
    { id: 'Web', label: 'Web', icon: Globe, description: 'Web search and real-time data' },
    { id: 'Vector', label: 'Vector', icon: Database, description: 'Vector database search' },
    { id: 'KG', label: 'KG', icon: Network, description: 'Knowledge graph traversal' },
    { id: 'Comprehensive', label: 'Comprehensive', icon: FileText, description: 'Deep analysis with citations' }
  ];

  const handleSearch = (query: string) => {
    try {
      setIsSearching(true);
      // Navigate to results page with the query
      router.push(`/search/results?q=${encodeURIComponent(query.trim())}&mode=${searchMode}`);
    } catch (error) {
      toast({
        title: "Search Error",
        description: "Failed to submit your query. Please try again.",
        variant: "destructive",
      });
    }
  };

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Intelligence",
      description: "Advanced AI models provide intelligent, contextual responses with deep understanding",
      color: "text-purple-400",
      bgColor: "bg-purple-500/10"
    },
    {
      icon: Globe,
      title: "Multi-Source Verification",
      description: "Verified information from diverse, reliable sources across the knowledge universe",
      color: "text-blue-400",
      bgColor: "bg-blue-500/10"
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Real-time processing with instant responses and live data integration",
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10"
    },
    {
      icon: Shield,
      title: "Trusted & Secure",
      description: "Enterprise-grade security with verified sources and fact-checking",
      color: "text-green-400",
      bgColor: "bg-green-500/10"
    }
  ];

  return (
    <div className="min-h-screen cosmic-bg-primary relative overflow-hidden">
      {/* Advanced cosmic background effects */}
      <StarField />
      <NebulaEffect />

      <div className="relative z-10 cosmic-container py-8">
        {/* Header - Industry Standard Spacing */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-16"
        >
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Sparkles className="h-10 w-10 text-cosmic-primary-500" />
              <div className="absolute -top-2 -right-2 w-4 h-4 bg-cosmic-primary-500 rounded-full animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 bg-clip-text text-transparent">
              SarvanOM
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <ThemeSelector />
            <ThemeToggle size="sm" />
          </div>
        </motion.div>

        {/* Main Search Interface - Industry Standard Layout */}
        <div className="max-w-6xl mx-auto text-center space-y-16">
          {/* Hero Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-8"
          >
            <div className="space-y-6">
              <h2 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-cosmic-text-primary via-cosmic-primary-500 to-cosmic-secondary-500 bg-clip-text text-transparent leading-tight">
                Universal Knowledge
              </h2>
              <p className="text-xl sm:text-2xl cosmic-text-secondary max-w-3xl mx-auto leading-relaxed">
                Ask anything. Get intelligent, verified answers from across the cosmos of knowledge.
              </p>
            </div>

            {/* Search Mode Pills */}
            <div className="flex flex-wrap justify-center gap-2 mb-8">
              {searchModes.map((mode) => (
                <motion.button
                  key={mode.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 + searchModes.indexOf(mode) * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSearchMode(mode.id as any)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    searchMode === mode.id
                      ? 'cosmic-btn-primary'
                      : 'cosmic-btn-secondary'
                  }`}
                  title={mode.description}
                >
                  <mode.icon className="w-4 h-4" />
                  {mode.label}
                </motion.button>
              ))}
            </div>

            {/* Search Form - Enhanced UX */}
            <div className="max-w-4xl mx-auto">
              {isSearching ? (
                <div className="cosmic-card p-8">
                  <StreamingSearch
                    onComplete={(data) => {
                      console.log('Search completed:', data);
                      setIsSearching(false);
                    }}
                    onError={(error) => {
                      console.error('Search error:', error);
                      setIsSearching(false);
                    }}
                    className="w-full"
                  />
                </div>
              ) : (
                <>
                  <MobileOptimizedSearch
                    onSearch={handleSearch}
                    placeholder="Ask anything about the universe, technology, science, or any topic..."
                    className="mb-8"
                  />
                  
                  {/* Quick Search Suggestions */}
                  <div className="flex flex-wrap justify-center gap-3 mt-6">
                    {[
                      "What is quantum computing?",
                      "Latest AI developments",
                      "Climate change solutions",
                      "Space exploration news"
                    ].map((suggestion, index) => (
                      <motion.button
                        key={suggestion}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.4 + index * 0.1 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleSearch(suggestion)}
                        className="px-4 py-2 text-sm cosmic-card hover:cosmic-hover-lift border border-cosmic-border-primary rounded-full cosmic-text-secondary hover:cosmic-text-primary transition-all duration-300 backdrop-blur-sm"
                      >
                        {suggestion}
                      </motion.button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </motion.div>

          {/* Features Grid - Industry Standard */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-12"
          >
            <div className="text-center space-y-4">
              <h3 className="text-3xl font-bold cosmic-text-primary">
                Why Choose SarvanOM?
              </h3>
              <p className="text-lg cosmic-text-secondary max-w-2xl mx-auto">
                Experience the next generation of knowledge discovery with cutting-edge AI technology
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="group cosmic-card backdrop-blur-sm border border-cosmic-border-primary rounded-2xl p-8 hover:cosmic-hover-lift transition-all duration-300 hover:shadow-xl hover:-translate-y-2"
                >
                  <div className="space-y-6">
                    <div className={`w-16 h-16 rounded-xl ${feature.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className={`w-8 h-8 ${feature.color}`} />
                    </div>
                    
                    <div className="space-y-4">
                      <h4 className="text-xl font-semibold cosmic-text-primary">
                        {feature.title}
                      </h4>
                      <p className="cosmic-text-secondary leading-relaxed text-sm">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Stats Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 py-12"
          >
            {[
              { number: "1M+", label: "Knowledge Sources" },
              { number: "99.9%", label: "Accuracy Rate" },
              { number: "<100ms", label: "Response Time" }
            ].map((stat, index) => (
              <div key={stat.label} className="text-center space-y-2">
                <div className="text-4xl font-bold text-cosmic-primary-500">
                  {stat.number}
                </div>
                <div className="cosmic-text-secondary">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
