"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  CalendarIcon,
  ClockIcon,
  UserIcon,
  TagIcon,
  ArrowRightIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  ShareIcon,
  HeartIcon
} from "@heroicons/react/24/outline";

interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  author: string;
  date: string;
  readTime: string;
  tags: string[];
  category: string;
  featured: boolean;
  likes: number;
  comments: number;
  image?: string;
}

export function EruditeBlog() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedPost, setSelectedPost] = useState<BlogPost | null>(null);

  const posts: BlogPost[] = [
    {
      id: "1",
      title: "The Future of AI-Powered Search: Beyond Keywords",
      excerpt: "Exploring how artificial intelligence is revolutionizing search beyond traditional keyword matching, enabling semantic understanding and contextual responses.",
      content: "The landscape of search technology has undergone a dramatic transformation in recent years. Traditional keyword-based search engines, while effective for simple queries, often fall short when users need nuanced, contextual information. This is where AI-powered search comes into play, offering a more intelligent and intuitive approach to information retrieval...",
      author: "Dr. Sarah Chen",
      date: "2024-01-15",
      readTime: "8 min read",
      tags: ["AI", "Search", "Machine Learning", "Technology"],
      category: "AI",
      featured: true,
      likes: 42,
      comments: 8
    },
    {
      id: "2",
      title: "Building Scalable Microservices with FastAPI",
      excerpt: "A comprehensive guide to creating robust, scalable microservices using FastAPI, including best practices for API design, testing, and deployment.",
      content: "FastAPI has emerged as one of the most popular frameworks for building modern web APIs. Its combination of high performance, automatic API documentation, and type safety makes it an excellent choice for microservices architecture...",
      author: "Alex Rodriguez",
      date: "2024-01-12",
      readTime: "12 min read",
      tags: ["FastAPI", "Python", "Microservices", "Backend"],
      category: "Development",
      featured: true,
      likes: 38,
      comments: 12
    },
    {
      id: "3",
      title: "The Art of Real-Time Data Streaming",
      excerpt: "Understanding Server-Sent Events and WebSockets for building responsive, real-time applications that keep users engaged.",
      content: "Real-time data streaming has become a cornerstone of modern web applications. From live chat systems to real-time analytics dashboards, the ability to push data to clients instantly has transformed user experiences...",
      author: "Maria Garcia",
      date: "2024-01-10",
      readTime: "6 min read",
      tags: ["WebSockets", "SSE", "Real-time", "JavaScript"],
      category: "Web Development",
      featured: false,
      likes: 29,
      comments: 5
    },
    {
      id: "4",
      title: "Designing Accessible User Interfaces",
      excerpt: "Best practices for creating inclusive, accessible web interfaces that work for everyone, regardless of their abilities or the devices they use.",
      content: "Accessibility in web design isn't just a nice-to-have feature—it's a fundamental requirement for creating inclusive digital experiences. With over 1 billion people worldwide living with some form of disability, designing accessible interfaces is both a moral imperative and a business necessity...",
      author: "Jordan Kim",
      date: "2024-01-08",
      readTime: "10 min read",
      tags: ["Accessibility", "UX", "Design", "Inclusion"],
      category: "Design",
      featured: false,
      likes: 35,
      comments: 7
    },
    {
      id: "5",
      title: "Quantum Computing: The Next Frontier",
      excerpt: "An introduction to quantum computing principles and their potential applications in solving complex computational problems.",
      content: "Quantum computing represents a paradigm shift in computational power, promising to solve problems that are intractable for classical computers. By harnessing the principles of quantum mechanics, quantum computers can process information in ways that fundamentally differ from traditional binary systems...",
      author: "Dr. Michael Thompson",
      date: "2024-01-05",
      readTime: "15 min read",
      tags: ["Quantum Computing", "Physics", "Technology", "Research"],
      category: "Science",
      featured: false,
      likes: 51,
      comments: 15
    }
  ];

  const categories = [
    { id: "all", label: "All Posts", count: posts.length },
    { id: "AI", label: "AI & ML", count: posts.filter(p => p.category === "AI").length },
    { id: "Development", label: "Development", count: posts.filter(p => p.category === "Development").length },
    { id: "Web Development", label: "Web Dev", count: posts.filter(p => p.category === "Web Development").length },
    { id: "Design", label: "Design", count: posts.filter(p => p.category === "Design").length },
    { id: "Science", label: "Science", count: posts.filter(p => p.category === "Science").length }
  ];

  const filteredPosts = posts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === "all" || post.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const featuredPosts = posts.filter(post => post.featured);
  const recentPosts = posts.slice(0, 3);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
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
              <BookOpenIcon className="w-4 h-4" />
              Erudite Blog
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">
              Knowledge & Insights
            </h1>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto mb-8">
              Deep dives into technology, AI, and the future of digital innovation. 
              Thoughtful articles for the curious mind.
            </p>
            
            {/* Search Bar */}
            <div className="max-w-md mx-auto relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </motion.div>
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
                      <span>{category.label}</span>
                      <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                        {category.count}
                      </span>
                    </button>
                  ))}
                </div>
              </motion.div>

              {/* Recent Posts */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold text-white mb-4">Recent Posts</h3>
                <div className="space-y-4">
                  {recentPosts.map((post) => (
                    <div key={post.id} className="group cursor-pointer">
                      <h4 className="text-white text-sm font-medium mb-1 group-hover:text-blue-400 transition-colors">
                        {post.title}
                      </h4>
                      <p className="text-gray-400 text-xs mb-2">{post.readTime}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <CalendarIcon className="w-3 h-3" />
                        {new Date(post.date).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Featured Posts */}
            {selectedCategory === "all" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="mb-8"
              >
                <h2 className="text-2xl font-bold text-white mb-6">Featured Articles</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {featuredPosts.map((post, index) => (
                    <motion.div
                      key={post.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6, delay: index * 0.1 }}
                      className="group cursor-pointer"
                      onClick={() => setSelectedPost(post)}
                    >
                      <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl overflow-hidden hover:bg-white/10 transition-all duration-300">
                        <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center">
                          <BookOpenIcon className="w-12 h-12 text-white/60" />
                        </div>
                        <div className="p-6">
                          <div className="flex items-center gap-2 mb-3">
                            <span className="px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs rounded">
                              {post.category}
                            </span>
                            <span className="text-gray-400 text-xs">{post.readTime}</span>
                          </div>
                          <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                            {post.title}
                          </h3>
                          <p className="text-gray-400 text-sm mb-4">{post.excerpt}</p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <UserIcon className="w-3 h-3" />
                                {post.author}
                              </div>
                              <div className="flex items-center gap-1">
                                <CalendarIcon className="w-3 h-3" />
                                {new Date(post.date).toLocaleDateString()}
                              </div>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <HeartIcon className="w-3 h-3" />
                                {post.likes}
                              </div>
                              <div className="flex items-center gap-1">
                                <ChatBubbleLeftRightIcon className="w-3 h-3" />
                                {post.comments}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* All Posts */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <h2 className="text-2xl font-bold text-white mb-6">
                {selectedCategory === "all" ? "All Articles" : `${selectedCategory} Articles`}
              </h2>
              <div className="space-y-6">
                {filteredPosts.map((post, index) => (
                  <motion.article
                    key={post.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="group cursor-pointer"
                    onClick={() => setSelectedPost(post)}
                  >
                    <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                      <div className="flex flex-col md:flex-row gap-6">
                        <div className="md:w-48 flex-shrink-0">
                          <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg flex items-center justify-center">
                            <BookOpenIcon className="w-8 h-8 text-white/60" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-3">
                            <span className="px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs rounded">
                              {post.category}
                            </span>
                            <span className="text-gray-400 text-xs">{post.readTime}</span>
                          </div>
                          <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                            {post.title}
                          </h3>
                          <p className="text-gray-400 text-sm mb-4">{post.excerpt}</p>
                          <div className="flex flex-wrap gap-2 mb-4">
                            {post.tags.map((tag) => (
                              <span key={tag} className="px-2 py-1 bg-white/10 text-white text-xs rounded">
                                #{tag}
                              </span>
                            ))}
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <UserIcon className="w-3 h-3" />
                                {post.author}
                              </div>
                              <div className="flex items-center gap-1">
                                <CalendarIcon className="w-3 h-3" />
                                {new Date(post.date).toLocaleDateString()}
                              </div>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <HeartIcon className="w-3 h-3" />
                                {post.likes}
                              </div>
                              <div className="flex items-center gap-1">
                                <ChatBubbleLeftRightIcon className="w-3 h-3" />
                                {post.comments}
                              </div>
                              <ArrowRightIcon className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.article>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Post Detail Modal */}
      {selectedPost && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedPost(null)}
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
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm rounded">
                    {selectedPost.category}
                  </span>
                  <span className="text-gray-400 text-sm">{selectedPost.readTime}</span>
                </div>
                <button
                  onClick={() => setSelectedPost(null)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>
              
              <h1 className="text-3xl font-bold text-white mb-4">{selectedPost.title}</h1>
              
              <div className="flex items-center gap-4 mb-6 text-gray-400 text-sm">
                <div className="flex items-center gap-1">
                  <UserIcon className="w-4 h-4" />
                  {selectedPost.author}
                </div>
                <div className="flex items-center gap-1">
                  <CalendarIcon className="w-4 h-4" />
                  {new Date(selectedPost.date).toLocaleDateString()}
                </div>
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  {selectedPost.readTime}
                </div>
              </div>

              <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg mb-6 flex items-center justify-center">
                <BookOpenIcon className="w-16 h-16 text-white/60" />
              </div>

              <div className="prose prose-invert max-w-none mb-6">
                <p className="text-gray-300 text-lg leading-relaxed">{selectedPost.content}</p>
              </div>

              <div className="flex flex-wrap gap-2 mb-6">
                {selectedPost.tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-white/10 text-white text-sm rounded">
                    #{tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-white/10">
                <div className="flex items-center gap-4 text-gray-400">
                  <button className="flex items-center gap-2 hover:text-white transition-colors">
                    <HeartIcon className="w-4 h-4" />
                    {selectedPost.likes}
                  </button>
                  <button className="flex items-center gap-2 hover:text-white transition-colors">
                    <ChatBubbleLeftRightIcon className="w-4 h-4" />
                    {selectedPost.comments}
                  </button>
                  <button className="flex items-center gap-2 hover:text-white transition-colors">
                    <ShareIcon className="w-4 h-4" />
                    Share
                  </button>
                </div>
                <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300">
                  Read Full Article
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
