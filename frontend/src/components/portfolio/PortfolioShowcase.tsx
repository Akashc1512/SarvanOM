"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  CodeBracketIcon,
  RocketLaunchIcon,
  CpuChipIcon,
  GlobeAltIcon,
  ChatBubbleLeftRightIcon,
  StarIcon,
  EyeIcon,
  ArrowTopRightOnSquareIcon,
  PlayIcon,
  PauseIcon
} from "@heroicons/react/24/outline";
import { SearchInput } from "@/components/search/SearchInput";

interface Project {
  id: string;
  title: string;
  description: string;
  longDescription: string;
  technologies: string[];
  image: string;
  liveUrl?: string;
  githubUrl?: string;
  category: "ai" | "web" | "mobile" | "data";
  featured: boolean;
  stats: {
    stars: number;
    forks: number;
    views: number;
  };
}

export default function PortfolioShowcase() {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [isPlaying, setIsPlaying] = useState(false);

  const projects: Project[] = [
    {
      id: "sarvanom",
      title: "SarvanOM Universal Knowledge Platform",
      description: "AI-powered search platform with real-time streaming and multi-source retrieval",
      longDescription: "A comprehensive knowledge platform that combines advanced AI capabilities with real-time streaming, hybrid search across multiple sources, and cosmic intelligence. Built with Next.js 15, FastAPI, and modern web technologies.",
      technologies: ["Next.js", "FastAPI", "TypeScript", "Tailwind CSS", "Zustand", "Server-Sent Events"],
      image: "/api/placeholder/600/400",
      liveUrl: "http://localhost:3000",
      category: "ai",
      featured: true,
      stats: { stars: 42, forks: 8, views: 1250 }
    },
    {
      id: "quantum-search",
      title: "Quantum Search Engine",
      description: "Next-generation search using quantum computing principles",
      longDescription: "An experimental search engine that leverages quantum computing principles for ultra-fast information retrieval and pattern matching across massive datasets.",
      technologies: ["Python", "Qiskit", "React", "WebGL", "TensorFlow"],
      image: "/api/placeholder/600/400",
      githubUrl: "https://github.com/example/quantum-search",
      category: "ai",
      featured: true,
      stats: { stars: 89, forks: 23, views: 2100 }
    },
    {
      id: "cosmic-analytics",
      title: "Cosmic Analytics Dashboard",
      description: "Real-time analytics with cosmic-themed visualizations",
      longDescription: "A beautiful analytics dashboard that transforms complex data into stunning cosmic visualizations, featuring real-time updates and interactive charts.",
      technologies: ["D3.js", "React", "WebSocket", "Chart.js", "Three.js"],
      image: "/api/placeholder/600/400",
      liveUrl: "https://cosmic-analytics.example.com",
      category: "web",
      featured: false,
      stats: { stars: 34, forks: 12, views: 890 }
    },
    {
      id: "neural-network-viz",
      title: "Neural Network Visualizer",
      description: "Interactive 3D visualization of neural network architectures",
      longDescription: "An immersive 3D visualization tool that allows users to explore neural network architectures, training processes, and data flow in real-time.",
      technologies: ["Three.js", "React", "WebGL", "TensorFlow.js", "Blender"],
      image: "/api/placeholder/600/400",
      githubUrl: "https://github.com/example/neural-viz",
      category: "ai",
      featured: false,
      stats: { stars: 156, forks: 45, views: 3200 }
    }
  ];

  const categories = [
    { id: "all", label: "All Projects", icon: GlobeAltIcon },
    { id: "ai", label: "AI & ML", icon: CpuChipIcon },
    { id: "web", label: "Web Apps", icon: CodeBracketIcon },
    { id: "mobile", label: "Mobile", icon: RocketLaunchIcon },
    { id: "data", label: "Data Science", icon: CpuChipIcon }
  ];

  const filteredProjects = activeCategory === "all" 
    ? projects 
    : projects.filter(project => project.category === activeCategory);

  const featuredProjects = projects.filter(project => project.featured);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section with Chatbot Integration */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl m-6 p-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
                <CpuChipIcon className="w-4 h-4" />
                AI Developer & Researcher
              </div>
              <h1 className="text-4xl font-bold text-white mb-4">
                Building the Future of
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                  Artificial Intelligence
                </span>
              </h1>
              <p className="text-lg text-gray-300 mb-8">
                Creating innovative AI solutions, interactive web experiences, and cutting-edge 
                technology that pushes the boundaries of what's possible.
              </p>
              <div className="flex flex-wrap gap-4">
                <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2">
                  <RocketLaunchIcon className="w-4 h-4" />
                  View Projects
                </button>
                <button className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300 flex items-center gap-2">
                  <ChatBubbleLeftRightIcon className="w-4 h-4" />
                  Chat with AI
                </button>
              </div>
            </motion.div>

            {/* Interactive Chatbot Interface */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-white text-sm ml-4">AI Assistant</span>
                </div>
                <div className="space-y-4">
                  <div className="bg-white/10 rounded-lg p-3">
                    <p className="text-white text-sm">
                      Hi! I'm your AI assistant. Ask me about my projects, technologies, or anything else!
                    </p>
                  </div>
                  <SearchInput 
                    placeholder="Ask about my work..."
                    className="w-full"
                  />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Featured Projects */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-4">Featured Projects</h2>
          <p className="text-gray-400">Showcasing my most impactful work</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          {featuredProjects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl blur-xl" />
              <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl overflow-hidden hover:bg-white/10 transition-all duration-300">
                <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center">
                  <PlayIcon className="w-16 h-16 text-white/60 group-hover:text-white transition-colors duration-300" />
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs rounded-full">
                      {project.category.toUpperCase()}
                    </span>
                    <div className="flex items-center gap-4 text-gray-400 text-sm">
                      <div className="flex items-center gap-1">
                        <StarIcon className="w-4 h-4" />
                        {project.stats.stars}
                      </div>
                      <div className="flex items-center gap-1">
                        <EyeIcon className="w-4 h-4" />
                        {project.stats.views}
                      </div>
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{project.title}</h3>
                  <p className="text-gray-400 text-sm mb-4">{project.description}</p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.technologies.slice(0, 3).map((tech) => (
                      <span key={tech} className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                        {tech}
                      </span>
                    ))}
                    {project.technologies.length > 3 && (
                      <span className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                        +{project.technologies.length - 3} more
                      </span>
                    )}
                  </div>
                  <div className="flex gap-3">
                    {project.liveUrl && (
                      <a
                        href={project.liveUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm"
                      >
                        <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                        Live Demo
                      </a>
                    )}
                    {project.githubUrl && (
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300 text-sm"
                      >
                        <CodeBracketIcon className="w-4 h-4" />
                        Code
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Project Categories */}
      <div className="max-w-7xl mx-auto px-6 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-4">All Projects</h2>
          <p className="text-gray-400">Explore my complete portfolio</p>
        </motion.div>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-300 ${
                activeCategory === category.id
                  ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                  : "bg-white/10 text-gray-300 hover:bg-white/20"
              }`}
            >
              <category.icon className="w-4 h-4" />
              {category.label}
            </button>
          ))}
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl blur-xl" />
              <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl overflow-hidden hover:bg-white/10 transition-all duration-300">
                <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center">
                  <PlayIcon className="w-12 h-12 text-white/60 group-hover:text-white transition-colors duration-300" />
                </div>
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs rounded">
                      {project.category.toUpperCase()}
                    </span>
                    <div className="flex items-center gap-2 text-gray-400 text-xs">
                      <StarIcon className="w-3 h-3" />
                      {project.stats.stars}
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{project.title}</h3>
                  <p className="text-gray-400 text-sm mb-3">{project.description}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {project.technologies.slice(0, 2).map((tech) => (
                      <span key={tech} className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                        {tech}
                      </span>
                    ))}
                    {project.technologies.length > 2 && (
                      <span className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                        +{project.technologies.length - 2}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {project.liveUrl && (
                      <a
                        href={project.liveUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm"
                      >
                        <ArrowTopRightOnSquareIcon className="w-3 h-3" />
                        Demo
                      </a>
                    )}
                    {project.githubUrl && (
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-white/10 text-white rounded hover:bg-white/20 transition-all duration-300 text-sm"
                      >
                        <CodeBracketIcon className="w-3 h-3" />
                        Code
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Project Detail Modal */}
      <AnimatePresence>
        {selectedProject && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedProject(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-3xl font-bold text-white">{selectedProject.title}</h2>
                  <button
                    onClick={() => setSelectedProject(null)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    ✕
                  </button>
                </div>
                <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg mb-6 flex items-center justify-center">
                  <PlayIcon className="w-20 h-20 text-white/60" />
                </div>
                <p className="text-gray-300 text-lg mb-6">{selectedProject.longDescription}</p>
                <div className="flex flex-wrap gap-2 mb-6">
                  {selectedProject.technologies.map((tech) => (
                    <span key={tech} className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm rounded">
                      {tech}
                    </span>
                  ))}
                </div>
                <div className="flex gap-4">
                  {selectedProject.liveUrl && (
                    <a
                      href={selectedProject.liveUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300"
                    >
                      <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                      View Live Demo
                    </a>
                  )}
                  {selectedProject.githubUrl && (
                    <a
                      href={selectedProject.githubUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300"
                    >
                      <CodeBracketIcon className="w-4 h-4" />
                      View Source Code
                    </a>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
