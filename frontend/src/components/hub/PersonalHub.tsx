"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  LinkIcon,
  CodeBracketIcon,
  RocketLaunchIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  GlobeAltIcon,
  HeartIcon,
  ShareIcon,
  ArrowTopRightOnSquareIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon
} from "@heroicons/react/24/outline";

interface LinkItem {
  id: string;
  title: string;
  url: string;
  description?: string;
  type: "website" | "project" | "social" | "document" | "media";
  category: string;
  isPublic: boolean;
  clicks: number;
  createdAt: string;
  tags: string[];
}

interface Category {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  color: string;
  count: number;
}

export function PersonalHub() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isAddingLink, setIsAddingLink] = useState(false);
  const [editingLink, setEditingLink] = useState<LinkItem | null>(null);

  const categories: Category[] = [
    { id: "all", name: "All Links", icon: LinkIcon, color: "from-blue-500 to-cyan-500", count: 0 },
    { id: "projects", name: "Projects", icon: CodeBracketIcon, color: "from-purple-500 to-pink-500", count: 0 },
    { id: "social", name: "Social", icon: ChatBubbleLeftRightIcon, color: "from-green-500 to-emerald-500", count: 0 },
    { id: "resources", name: "Resources", icon: DocumentTextIcon, color: "from-orange-500 to-red-500", count: 0 },
    { id: "media", name: "Media", icon: PhotoIcon, color: "from-indigo-500 to-purple-500", count: 0 }
  ];

  const [links, setLinks] = useState<LinkItem[]>([
    {
      id: "1",
      title: "SarvanOM Platform",
      url: "http://localhost:3000",
      description: "AI-powered universal knowledge platform with real-time streaming",
      type: "project",
      category: "projects",
      isPublic: true,
      clicks: 234,
      createdAt: "2024-01-15",
      tags: ["AI", "Search", "Next.js", "FastAPI"]
    },
    {
      id: "2",
      title: "GitHub Profile",
      url: "https://github.com/username",
      description: "My open-source projects and contributions",
      type: "social",
      category: "social",
      isPublic: true,
      clicks: 189,
      createdAt: "2024-01-10",
      tags: ["GitHub", "Open Source", "Code"]
    },
    {
      id: "3",
      title: "Portfolio Website",
      url: "https://portfolio.example.com",
      description: "Personal portfolio showcasing my work and skills",
      type: "website",
      category: "projects",
      isPublic: true,
      clicks: 156,
      createdAt: "2024-01-08",
      tags: ["Portfolio", "React", "Design"]
    },
    {
      id: "4",
      title: "LinkedIn Profile",
      url: "https://linkedin.com/in/username",
      description: "Professional network and career updates",
      type: "social",
      category: "social",
      isPublic: true,
      clicks: 98,
      createdAt: "2024-01-05",
      tags: ["Professional", "Networking", "Career"]
    },
    {
      id: "5",
      title: "AI Research Paper",
      url: "https://arxiv.org/abs/example",
      description: "Latest research on quantum machine learning",
      type: "document",
      category: "resources",
      isPublic: true,
      clicks: 67,
      createdAt: "2024-01-03",
      tags: ["Research", "AI", "Quantum", "ML"]
    },
    {
      id: "6",
      title: "Tech Talk Video",
      url: "https://youtube.com/watch?v=example",
      description: "Presentation on the future of AI-powered search",
      type: "media",
      category: "media",
      isPublic: true,
      clicks: 145,
      createdAt: "2024-01-01",
      tags: ["Video", "Presentation", "AI", "Tech"]
    }
  ]);

  // Update category counts
  categories.forEach(category => {
    if (category.id === "all") {
      category.count = links.length;
    } else {
      category.count = links.filter(link => link.category === category.id).length;
    }
  });

  const filteredLinks = selectedCategory === "all" 
    ? links 
    : links.filter(link => link.category === selectedCategory);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "website": return GlobeAltIcon;
      case "project": return CodeBracketIcon;
      case "social": return ChatBubbleLeftRightIcon;
      case "document": return DocumentTextIcon;
      case "media": return PhotoIcon;
      default: return LinkIcon;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "website": return "from-blue-500 to-cyan-500";
      case "project": return "from-purple-500 to-pink-500";
      case "social": return "from-green-500 to-emerald-500";
      case "document": return "from-orange-500 to-red-500";
      case "media": return "from-indigo-500 to-purple-500";
      default: return "from-gray-500 to-gray-600";
    }
  };

  const handleLinkClick = (linkId: string) => {
    setLinks(prev => prev.map(link => 
      link.id === linkId 
        ? { ...link, clicks: link.clicks + 1 }
        : link
    ));
  };

  const handleDeleteLink = (linkId: string) => {
    setLinks(prev => prev.filter(link => link.id !== linkId));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl m-6 p-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-4">
                <LinkIcon className="w-4 h-4" />
                Personal Hub
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">
                My Digital Space
              </h1>
              <p className="text-lg text-gray-300">
                A curated collection of my projects, resources, and online presence
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex gap-4"
            >
              <button
                onClick={() => setIsAddingLink(true)}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2"
              >
                <PlusIcon className="w-4 h-4" />
                Add Link
              </button>
              <button className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300 flex items-center gap-2">
                <ShareIcon className="w-4 h-4" />
                Share Hub
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Categories */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold text-white mb-4">Categories</h3>
                <div className="space-y-2">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full flex items-center justify-between p-3 rounded-lg transition-all duration-300 ${
                        selectedCategory === category.id
                          ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                          : "bg-white/5 text-gray-300 hover:bg-white/10"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <category.icon className="w-4 h-4" />
                        <span>{category.name}</span>
                      </div>
                      <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                        {category.count}
                      </span>
                    </button>
                  ))}
                </div>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold text-white mb-4">Hub Stats</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">Total Links</span>
                    <span className="text-white font-medium">{links.length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">Total Clicks</span>
                    <span className="text-white font-medium">
                      {links.reduce((sum, link) => sum + link.clicks, 0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 text-sm">Public Links</span>
                    <span className="text-white font-medium">
                      {links.filter(link => link.isPublic).length}
                    </span>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Links Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">
                  {selectedCategory === "all" ? "All Links" : `${categories.find(c => c.id === selectedCategory)?.name}`}
                </h2>
                <div className="text-gray-400 text-sm">
                  {filteredLinks.length} link{filteredLinks.length !== 1 ? 's' : ''}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredLinks.map((link, index) => {
                  const TypeIcon = getTypeIcon(link.type);
                  const typeColor = getTypeColor(link.type);
                  
                  return (
                    <motion.div
                      key={link.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, delay: index * 0.1 }}
                      className="group relative"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl"
                           style={{ backgroundImage: `linear-gradient(to right, ${typeColor})` }} />
                      <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                        <div className="flex items-start justify-between mb-4">
                          <div className={`p-3 rounded-xl bg-gradient-to-r ${typeColor}`}>
                            <TypeIcon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => setEditingLink(link)}
                              className="p-2 text-gray-400 hover:text-white transition-colors"
                            >
                              <PencilIcon className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteLink(link.id)}
                              className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                            >
                              <TrashIcon className="w-4 h-4" />
                            </button>
                          </div>
                        </div>

                        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                          {link.title}
                        </h3>
                        
                        {link.description && (
                          <p className="text-gray-400 text-sm mb-4">{link.description}</p>
                        )}

                        <div className="flex flex-wrap gap-2 mb-4">
                          {link.tags.slice(0, 3).map((tag) => (
                            <span key={tag} className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                              #{tag}
                            </span>
                          ))}
                          {link.tags.length > 3 && (
                            <span className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                              +{link.tags.length - 3}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <div className="flex items-center gap-1">
                              <HeartIcon className="w-3 h-3" />
                              {link.clicks} clicks
                            </div>
                            <div className="flex items-center gap-1">
                              <span>{new Date(link.createdAt).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <a
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={() => handleLinkClick(link.id)}
                            className="flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm"
                          >
                            <ArrowTopRightOnSquareIcon className="w-3 h-3" />
                            Visit
                          </a>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {filteredLinks.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <LinkIcon className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">No links found</h3>
                  <p className="text-gray-400 mb-6">
                    {selectedCategory === "all" 
                      ? "Start building your personal hub by adding your first link."
                      : `No links in the ${categories.find(c => c.id === selectedCategory)?.name.toLowerCase()} category.`
                    }
                  </p>
                  <button
                    onClick={() => setIsAddingLink(true)}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2 mx-auto"
                  >
                    <PlusIcon className="w-4 h-4" />
                    Add Your First Link
                  </button>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>
      </div>

      {/* Add/Edit Link Modal */}
      {(isAddingLink || editingLink) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => {
            setIsAddingLink(false);
            setEditingLink(null);
          }}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">
                {editingLink ? "Edit Link" : "Add New Link"}
              </h3>
              <button
                onClick={() => {
                  setIsAddingLink(false);
                  setEditingLink(null);
                }}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-white text-sm font-medium mb-2">Title</label>
                <input
                  type="text"
                  defaultValue={editingLink?.title || ""}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter link title"
                />
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-2">URL</label>
                <input
                  type="url"
                  defaultValue={editingLink?.url || ""}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com"
                />
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-2">Description</label>
                <textarea
                  defaultValue={editingLink?.description || ""}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of the link"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-2">Category</label>
                <select
                  defaultValue={editingLink?.category || "projects"}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.filter(c => c.id !== "all").map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setIsAddingLink(false);
                    setEditingLink(null);
                  }}
                  className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300"
                >
                  {editingLink ? "Update" : "Add"} Link
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
