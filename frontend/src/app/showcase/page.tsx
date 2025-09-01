"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  SparklesIcon,
  CodeBracketIcon,
  ChartBarIcon,
  BookOpenIcon,
  RocketLaunchIcon,
  LinkIcon,
  EyeIcon,
  ArrowRightIcon
} from "@heroicons/react/24/outline";

// Import all the theme-inspired components
import { ThemeShowcase } from "@/components/ui/theme-showcase";
import { PortfolioShowcase } from "@/components/portfolio/PortfolioShowcase";
import { DataNovaDashboard } from "@/components/analytics/DataNovaDashboard";
import { EruditeBlog } from "@/components/blog/EruditeBlog";
import { BlackspikeLanding } from "@/components/landing/BlackspikeLanding";
import { PersonalHub } from "@/components/hub/PersonalHub";

const components = [
  {
    id: "theme-showcase",
    name: "Theme Showcase",
    description: "Overview of all Astro-inspired components",
    icon: SparklesIcon,
    component: ThemeShowcase,
    color: "from-blue-500 to-cyan-500"
  },
  {
    id: "portfolio",
    name: "Portfolio Showcase",
    description: "Inspired by macos-portfolio-extended with chatbot integration",
    icon: CodeBracketIcon,
    component: PortfolioShowcase,
    color: "from-purple-500 to-pink-500"
  },
  {
    id: "analytics",
    name: "Analytics Dashboard",
    description: "Inspired by DataNova with comprehensive metrics",
    icon: ChartBarIcon,
    component: DataNovaDashboard,
    color: "from-green-500 to-emerald-500"
  },
  {
    id: "blog",
    name: "Erudite Blog",
    description: "Inspired by astro-erudite with clean, minimal design",
    icon: BookOpenIcon,
    component: EruditeBlog,
    color: "from-orange-500 to-red-500"
  },
  {
    id: "landing",
    name: "Landing Page",
    description: "Inspired by blackspike astro with modern design",
    icon: RocketLaunchIcon,
    component: BlackspikeLanding,
    color: "from-indigo-500 to-purple-500"
  },
  {
    id: "hub",
    name: "Personal Hub",
    description: "Inspired by Personal Hub theme for link management",
    icon: LinkIcon,
    component: PersonalHub,
    color: "from-teal-500 to-blue-500"
  }
];

export default function ShowcasePage() {
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  const selectedComponentData = components.find(c => c.id === selectedComponent);
  const SelectedComponent = selectedComponentData?.component;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {!selectedComponent ? (
        <>
          {/* Header */}
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
                  Astro Themes Reimagined
                </div>
                <h1 className="text-5xl font-bold text-white mb-6">
                  Next.js Component
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                    Showcase
                  </span>
                </h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
                  Experience the best of Astro themes reimagined for Next.js 15. 
                  Each component maintains the original design philosophy while adding 
                  modern React features, real-time capabilities, and enhanced interactivity.
                </p>
              </motion.div>
            </div>
          </div>

          {/* Components Grid */}
          <div className="max-w-7xl mx-auto px-6 py-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl font-bold text-white mb-4">Available Components</h2>
              <p className="text-gray-400">Click on any component to explore it in detail</p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {components.map((component, index) => (
                <motion.div
                  key={component.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="group cursor-pointer"
                  onClick={() => setSelectedComponent(component.id)}
                >
                  <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl"
                       style={{ backgroundImage: `linear-gradient(to right, ${component.color})` }} />
                  <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                    <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${component.color} mb-4`}>
                      <component.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                      {component.name}
                    </h3>
                    <p className="text-gray-400 text-sm mb-4 leading-relaxed">
                      {component.description}
                    </p>
                    <div className="flex items-center gap-2 text-blue-400 text-sm font-medium">
                      <span>Explore Component</span>
                      <ArrowRightIcon className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Features Comparison */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="mt-20"
            >
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-white mb-4">Why Next.js Over Astro?</h2>
                <p className="text-gray-400">Enhanced capabilities while maintaining design excellence</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-8">
                  <h3 className="text-xl font-semibold text-white mb-4">Astro Themes</h3>
                  <ul className="space-y-3 text-gray-400">
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                      Static site generation
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                      Limited interactivity
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                      No real-time features
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                      Basic state management
                    </li>
                  </ul>
                </div>

                <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-8">
                  <h3 className="text-xl font-semibold text-white mb-4">Our Next.js Implementation</h3>
                  <ul className="space-y-3 text-gray-400">
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      Full-stack capabilities
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      Real-time streaming
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      Advanced state management
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      AI-powered features
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      ) : (
        <>
          {/* Component Header */}
          <div className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
            <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl m-6 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setSelectedComponent(null)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    ← Back
                  </button>
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${selectedComponentData?.color}`}>
                    {selectedComponentData?.icon && <selectedComponentData.icon className="w-6 h-6 text-white" />}
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">{selectedComponentData?.name}</h1>
                    <p className="text-gray-400">{selectedComponentData?.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  <EyeIcon className="w-4 h-4" />
                  <span>Live Preview</span>
                </div>
              </div>
            </div>
          </div>

          {/* Component Content */}
          <div className="pb-8">
            {SelectedComponent && <SelectedComponent />}
          </div>
        </>
      )}
    </div>
  );
}
