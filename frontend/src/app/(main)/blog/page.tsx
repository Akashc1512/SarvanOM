"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MagnifyingGlassIcon,
  CalendarIcon,
  UserIcon,
  TagIcon,
  ArrowRightIcon,
  ClockIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Badge } from '@/ui/ui/badge';
import { Input } from '@/ui/ui/input';
import { cn } from '@/lib/utils';

interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  author: string;
  date: string;
  readTime: string;
  tags: string[];
  image?: string;
  views: number;
  likes: number;
  featured?: boolean;
}

// Metadata removed - this is a client component

export default function BlogPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const blogPosts: BlogPost[] = [
    {
      id: '1',
      title: 'The Future of AI-Powered Knowledge Management',
      excerpt: 'Exploring how artificial intelligence is revolutionizing the way we organize, search, and interact with information in the digital age.',
      content: 'Full article content...',
      author: 'Dr. Sarah Chen',
      date: '2024-01-15',
      readTime: '8 min read',
      tags: ['AI', 'Knowledge Management', 'Technology'],
      views: 1247,
      likes: 89,
      featured: true
    },
    {
      id: '2',
      title: 'Building Scalable Vector Databases for Enterprise',
      excerpt: 'A deep dive into the architecture and implementation of vector databases that can handle millions of embeddings efficiently.',
      content: 'Full article content...',
      author: 'Michael Rodriguez',
      date: '2024-01-12',
      readTime: '12 min read',
      tags: ['Vector Databases', 'Enterprise', 'Architecture'],
      views: 892,
      likes: 67
    },
    {
      id: '3',
      title: 'Real-time Streaming with Server-Sent Events',
      excerpt: 'Learn how to implement real-time data streaming in web applications using SSE for optimal user experience.',
      content: 'Full article content...',
      author: 'Emily Watson',
      date: '2024-01-10',
      readTime: '6 min read',
      tags: ['Web Development', 'Real-time', 'SSE'],
      views: 654,
      likes: 43
    },
    {
      id: '4',
      title: 'The Art of Prompt Engineering for LLMs',
      excerpt: 'Master the techniques of crafting effective prompts to get the best results from large language models.',
      content: 'Full article content...',
      author: 'Alex Thompson',
      date: '2024-01-08',
      readTime: '10 min read',
      tags: ['LLM', 'Prompt Engineering', 'AI'],
      views: 1123,
      likes: 156
    },
    {
      id: '5',
      title: 'Microservices Architecture for AI Applications',
      excerpt: 'Designing and implementing microservices architecture specifically tailored for AI-powered applications.',
      content: 'Full article content...',
      author: 'David Kim',
      date: '2024-01-05',
      readTime: '15 min read',
      tags: ['Microservices', 'AI', 'Architecture'],
      views: 743,
      likes: 92
    },
    {
      id: '6',
      title: 'Understanding Knowledge Graphs in Practice',
      excerpt: 'Practical applications and implementation strategies for knowledge graphs in modern applications.',
      content: 'Full article content...',
      author: 'Lisa Park',
      date: '2024-01-03',
      readTime: '9 min read',
      tags: ['Knowledge Graphs', 'Data Science', 'Graph Theory'],
      views: 567,
      likes: 78
    }
  ];

  const allTags = Array.from(new Set(blogPosts.flatMap(post => post.tags)));

  const filteredPosts = blogPosts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesTag = !selectedTag || post.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  const featuredPost = blogPosts.find(post => post.featured);
  const regularPosts = filteredPosts.filter(post => !post.featured);

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl font-bold cosmic-text-primary mb-4">
              Knowledge Blog
            </h1>
            <p className="text-lg cosmic-text-secondary max-w-3xl mx-auto">
              Insights, tutorials, and deep dives into AI, knowledge management, and modern software architecture.
            </p>
          </motion.div>

          {/* Search and Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-8"
          >
            <Card className="cosmic-card">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-cosmic-text-tertiary" />
                      <Input
                        placeholder="Search articles..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 cosmic-input"
                      />
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={selectedTag === null ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedTag(null)}
                      className={selectedTag === null ? "cosmic-btn-primary" : "cosmic-btn-secondary"}
                    >
                      All
                    </Button>
                    {allTags.map((tag) => (
                      <Button
                        key={tag}
                        variant={selectedTag === tag ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                        className={selectedTag === tag ? "cosmic-btn-primary" : "cosmic-btn-secondary"}
                      >
                        {tag}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Featured Post */}
          {featuredPost && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="mb-12"
            >
              <Card className="cosmic-card overflow-hidden">
                <div className="grid md:grid-cols-2 gap-0">
                  <div className="p-8">
                    <div className="flex items-center gap-2 mb-4">
                      <Badge variant="outline" className="border-cosmic-primary-500 text-cosmic-primary-500">
                        Featured
                      </Badge>
                      <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                        {featuredPost.readTime}
                      </Badge>
                    </div>
                    <h2 className="text-2xl font-bold cosmic-text-primary mb-4">
                      {featuredPost.title}
                    </h2>
                    <p className="cosmic-text-secondary mb-6">
                      {featuredPost.excerpt}
                    </p>
                    <div className="flex items-center gap-4 text-sm cosmic-text-tertiary mb-6">
                      <div className="flex items-center gap-1">
                        <UserIcon className="h-4 w-4" />
                        {featuredPost.author}
                      </div>
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        {new Date(featuredPost.date).toLocaleDateString()}
                      </div>
                      <div className="flex items-center gap-1">
                        <EyeIcon className="h-4 w-4" />
                        {featuredPost.views}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mb-6">
                      {featuredPost.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <Button className="cosmic-btn-primary">
                      Read Article
                      <ArrowRightIcon className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                  <div className="cosmic-bg-secondary flex items-center justify-center p-8">
                    <div className="text-center">
                      <div className="w-24 h-24 bg-cosmic-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <TagIcon className="h-12 w-12 text-cosmic-primary-500" />
                      </div>
                      <p className="cosmic-text-secondary">Featured Article</p>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Posts Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {regularPosts.map((post, index) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 * index }}
              >
                <Card className="cosmic-card h-full hover:cosmic-card-elevated transition-all duration-200">
                  <CardHeader>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary text-xs">
                        {post.readTime}
                      </Badge>
                    </div>
                    <CardTitle className="cosmic-text-primary line-clamp-2">
                      {post.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="cosmic-text-secondary mb-4 line-clamp-3">
                      {post.excerpt}
                    </p>
                    
                    <div className="flex items-center gap-4 text-sm cosmic-text-tertiary mb-4">
                      <div className="flex items-center gap-1">
                        <UserIcon className="h-4 w-4" />
                        {post.author}
                      </div>
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        {new Date(post.date).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 mb-4">
                      {post.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {post.tags.length > 2 && (
                        <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary text-xs">
                          +{post.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm cosmic-text-tertiary">
                        <div className="flex items-center gap-1">
                          <EyeIcon className="h-4 w-4" />
                          {post.views}
                        </div>
                        <div className="flex items-center gap-1">
                          <HeartIcon className="h-4 w-4" />
                          {post.likes}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" className="cosmic-btn-secondary">
                        <ShareIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Load More */}
          {filteredPosts.length > 6 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="text-center mt-12"
            >
              <Button variant="outline" className="cosmic-btn-secondary">
                Load More Articles
              </Button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
