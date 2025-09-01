"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Brain, Globe, Search, Zap, Shield } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { StarField, NebulaEffect } from "@/ui/CosmicParticles";
import { ThemeSelector } from "@/ui/ThemeSelector";
import { ThemeToggle } from "@/ui/ThemeToggle";
import { MobileOptimizedSearch } from "@/ui/MobileOptimizedSearch";
import { useToast } from "@/hooks/useToast";
import { motion } from "framer-motion";

export default function SearchPage() {
  const router = useRouter();
  const { toast } = useToast();

  const handleSearch = (query: string) => {
    try {
      // Navigate to results page with the query
      router.push(`/search/results?q=${encodeURIComponent(query.trim())}`);
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
    <div className="min-h-screen bg-cosmos-bg relative overflow-hidden">
      {/* Advanced cosmic background effects */}
      <StarField />
      <NebulaEffect />

      <div className="relative z-10 container mx-auto px-6 sm:px-8 lg:px-12 py-8">
        {/* Header - Industry Standard Spacing */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-16"
        >
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Sparkles className="h-10 w-10 text-cosmos-accent" />
              <div className="absolute -top-2 -right-2 w-4 h-4 bg-cosmos-accent rounded-full animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cosmos-accent to-blue-400 bg-clip-text text-transparent">
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
              <h2 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-cosmos-fg via-cosmos-accent to-blue-400 bg-clip-text text-transparent leading-tight">
                Universal Knowledge
              </h2>
              <p className="text-xl sm:text-2xl text-cosmos-fg/80 max-w-3xl mx-auto leading-relaxed">
                Ask anything. Get intelligent, verified answers from across the cosmos of knowledge.
              </p>
            </div>

            {/* Search Form - Enhanced UX */}
            <div className="max-w-4xl mx-auto">
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
                    className="px-4 py-2 text-sm bg-cosmos-card/50 hover:bg-cosmos-card/70 border border-cosmos-accent/20 rounded-full text-cosmos-fg/80 hover:text-cosmos-fg transition-all duration-300 backdrop-blur-sm"
                  >
                    {suggestion}
                  </motion.button>
                ))}
              </div>
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
              <h3 className="text-3xl font-bold text-cosmos-fg">
                Why Choose SarvanOM?
              </h3>
              <p className="text-lg text-cosmos-fg/70 max-w-2xl mx-auto">
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
                  className="group bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl p-8 hover:bg-cosmos-card/70 transition-all duration-300 hover:shadow-xl hover:-translate-y-2"
                >
                  <div className="space-y-6">
                    <div className={`w-16 h-16 rounded-xl ${feature.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className={`w-8 h-8 ${feature.color}`} />
                    </div>
                    
                    <div className="space-y-4">
                      <h4 className="text-xl font-semibold text-cosmos-fg">
                        {feature.title}
                      </h4>
                      <p className="text-cosmos-fg/70 leading-relaxed text-sm">
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
                <div className="text-4xl font-bold text-cosmos-accent">
                  {stat.number}
                </div>
                <div className="text-cosmos-fg/70">
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
