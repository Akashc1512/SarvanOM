"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  SparklesIcon, 
  CodeBracketIcon, 
  RocketLaunchIcon,
  CpuChipIcon,
  GlobeAltIcon,
  ChatBubbleLeftRightIcon
} from "@heroicons/react/24/outline";

// Inspired by Astro themes but built for Next.js
export function ThemeShowcase() {
  const features = [
    {
      icon: ChatBubbleLeftRightIcon,
      title: "AI Chat Integration",
      description: "Real-time streaming responses with multiple LLM providers",
      color: "from-blue-500 to-purple-600"
    },
    {
      icon: CpuChipIcon,
      title: "Advanced Analytics",
      description: "Comprehensive search analytics and performance metrics",
      color: "from-green-500 to-teal-600"
    },
    {
      icon: GlobeAltIcon,
      title: "Multi-Source Search",
      description: "Hybrid search across documents, web, and knowledge graphs",
      color: "from-orange-500 to-red-600"
    },
    {
      icon: RocketLaunchIcon,
      title: "Real-time Streaming",
      description: "Server-Sent Events for live answer generation",
      color: "from-purple-500 to-pink-600"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Glassmorphism Header - Inspired by Modern Developer Portfolio */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl m-6 p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
              <SparklesIcon className="w-4 h-4" />
              Next-Gen AI Platform
            </div>
            <h1 className="text-5xl font-bold text-white mb-6">
              SarvanOM
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                Universal Knowledge
              </span>
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
              Advanced AI-powered search with real-time streaming, multi-source retrieval, 
              and cosmic intelligence - built with Next.js 15 and modern web standards.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Feature Grid - Inspired by Personal Hub */}
      <div className="max-w-7xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl"
                   style={{ backgroundImage: `linear-gradient(to right, ${feature.color})` }} />
              <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Tech Stack - Inspired by AstroLaunch UI */}
      <div className="max-w-4xl mx-auto px-6 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-8"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-4">
              Built with Modern Technology
            </h2>
            <p className="text-gray-400">
              Leveraging the latest web technologies for optimal performance
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: "Next.js 15", icon: "⚡" },
              { name: "React 18", icon: "⚛️" },
              { name: "Tailwind CSS", icon: "🎨" },
              { name: "FastAPI", icon: "🚀" },
              { name: "TypeScript", icon: "📘" },
              { name: "Zustand", icon: "🏪" },
              { name: "Framer Motion", icon: "✨" },
              { name: "Server-Sent Events", icon: "📡" }
            ].map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="text-center group"
              >
                <div className="text-4xl mb-2 group-hover:scale-110 transition-transform duration-300">
                  {tech.icon}
                </div>
                <div className="text-white font-medium text-sm">
                  {tech.name}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
