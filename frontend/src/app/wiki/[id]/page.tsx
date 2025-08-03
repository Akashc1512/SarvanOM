"use client";

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Badge } from '@/ui/ui/badge';
import { Alert, AlertDescription } from '@/ui/ui/alert';
import { Loader2, ArrowLeft, Edit, Calendar, User, Eye, Tag } from 'lucide-react';

interface WikiArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  author?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
  read_count?: number;
}

export default function WikiArticle({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [article, setArticle] = useState<WikiArticle | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticle();
  }, [params.id]);

  const fetchArticle = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`/api/wiki/${params.id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setArticle(data);
    } catch (err) {
      console.error('Error fetching wiki article:', err);
      setError(err instanceof Error ? err.message : 'Failed to load article');
      
      // Mock data for development/testing
      if (params.id === '1') {
        setArticle({
          id: '1',
          title: 'Getting Started with SarvanOM',
          content: `# Getting Started with SarvanOM

## Introduction

SarvanOM is a comprehensive knowledge platform that combines AI-powered insights with collaborative document management for enterprise teams.

## Key Features

### 1. AI-Powered Search
- Natural language querying
- Semantic search capabilities
- Intelligent result ranking

### 2. Knowledge Graph Integration
- Entity relationship mapping
- Contextual information retrieval
- Dynamic knowledge connections

### 3. Collaborative Features
- Real-time editing
- Version control
- Team collaboration tools

## Getting Started

### Step 1: Access the Platform
1. Navigate to the main dashboard
2. Use your credentials to log in
3. Familiarize yourself with the interface

### Step 2: Create Your First Query
1. Click on "New Query" in the navigation
2. Enter your question in natural language
3. Review the AI-generated response
4. Check citations and sources

### Step 3: Explore the Knowledge Base
1. Browse existing articles
2. Search for specific topics
3. Contribute to the knowledge base

## Best Practices

- Use clear, descriptive titles for your queries
- Review and validate AI responses
- Contribute to the knowledge base regularly
- Collaborate with team members

## Support

For additional help, contact the platform administrators or consult the advanced documentation.`,
          summary: 'Learn the basics of using the SarvanOM knowledge platform for your organization.',
          author: 'Admin',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-20T14:30:00Z',
          tags: ['guide', 'beginner'],
          read_count: 156
        });
      } else if (params.id === '2') {
        setArticle({
          id: '2',
          title: 'Advanced Query Techniques',
          content: `# Advanced Query Techniques

## Overview

Master advanced querying techniques to get the most out of your knowledge base.

## Advanced Search Operators

### Boolean Operators
- Use AND, OR, NOT for complex queries
- Combine multiple search terms effectively
- Filter results by specific criteria

### Phrase Searching
- Use quotes for exact phrase matching
- Maintain word order and proximity
- Improve search precision

### Wildcard Searches
- Use * for partial word matching
- Expand search scope efficiently
- Find related terms and variations

## Query Optimization

### 1. Specificity
- Be as specific as possible
- Use technical terms when appropriate
- Avoid overly broad queries

### 2. Context
- Provide relevant context
- Include domain-specific terminology
- Reference related concepts

### 3. Iteration
- Refine queries based on results
- Learn from search patterns
- Improve over time

## Advanced Features

### Semantic Search
- Leverage AI understanding
- Find conceptually related content
- Discover hidden connections

### Knowledge Graph Queries
- Explore entity relationships
- Navigate connected information
- Discover new insights

## Tips for Success

1. Start with simple queries and refine
2. Use the platform's suggestions
3. Explore related content
4. Save useful queries for future use
5. Share effective query patterns with your team`,
          summary: 'Master advanced querying techniques to get the most out of your knowledge base.',
          author: 'Expert User',
          created_at: '2024-01-10T09:00:00Z',
          updated_at: '2024-01-18T16:45:00Z',
          tags: ['advanced', 'queries'],
          read_count: 89
        });
      } else if (params.id === '3') {
        setArticle({
          id: '3',
          title: 'API Integration Guide',
          content: `# API Integration Guide

## Introduction

Complete guide for integrating SarvanOM APIs into your applications.

## Authentication

### API Keys
- Generate API keys from the admin dashboard
- Include keys in request headers
- Rotate keys regularly for security

### OAuth 2.0
- Implement OAuth flow for user authentication
- Handle token refresh automatically
- Secure user data access

## Core Endpoints

### Query API
\`\`\`javascript
POST /api/query
{
  "query": "your question here",
  "max_tokens": 1000,
  "confidence_threshold": 0.8
}
\`\`\`

### Search API
\`\`\`javascript
GET /api/search?q=search+terms&limit=10
\`\`\`

### Knowledge Graph API
\`\`\`javascript
GET /api/knowledge-graph/entities/{entity_id}
\`\`\`

## Response Formats

### Query Response
\`\`\`json
{
  "answer": "AI-generated response",
  "confidence": 0.95,
  "citations": [...],
  "query_id": "uuid",
  "processing_time": 1.2
}
\`\`\`

### Error Handling
\`\`\`json
{
  "error": "Error message",
  "status_code": 400,
  "details": "Additional information"
}
\`\`\`

## Rate Limiting

- 100 requests per minute per API key
- Implement exponential backoff
- Monitor usage and adjust accordingly

## Best Practices

1. Cache responses when appropriate
2. Handle errors gracefully
3. Implement retry logic
4. Monitor API usage
5. Keep SDKs updated

## SDKs and Libraries

- JavaScript/TypeScript SDK available
- Python client library
- REST API documentation
- Postman collection provided`,
          summary: 'Complete guide for integrating SarvanOM APIs into your applications.',
          author: 'Developer',
          created_at: '2024-01-05T11:00:00Z',
          updated_at: '2024-01-12T13:20:00Z',
          tags: ['api', 'integration', 'technical'],
          read_count: 234
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderMarkdown = (content: string) => {
    // Simple markdown rendering - in a real app, you'd use a proper markdown library
    return content
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-6 mb-3">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto"><code>$2</code></pre>')
      .replace(/\n/g, '<br>');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading article...</span>
        </div>
      </div>
    );
  }

  if (error && !article) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link href="/wiki" className="flex items-center text-blue-600 hover:text-blue-800 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Wiki
          </Link>
        </div>
        
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
        
        <div className="mt-4">
          <Button onClick={() => router.push('/wiki')} variant="outline">
            Return to Wiki
          </Button>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link href="/wiki" className="flex items-center text-blue-600 hover:text-blue-800 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Wiki
          </Link>
        </div>
        
        <Alert>
          <AlertDescription>
            Article not found. It may have been deleted or moved.
          </AlertDescription>
        </Alert>
        
        <div className="mt-4">
          <Button onClick={() => router.push('/wiki')} variant="outline">
            Return to Wiki
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link href="/wiki" className="flex items-center text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Wiki
        </Link>
        
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {article.title}
            </h1>
            {article.summary && (
              <p className="text-gray-600 text-lg mb-4">
                {article.summary}
              </p>
            )}
          </div>
          
          <div className="flex space-x-2">
            <Link href={`/wiki/${article.id}/edit`}>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Article Meta Information */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
            {article.author && (
              <div className="flex items-center space-x-1">
                <User className="h-4 w-4" />
                <span>{article.author}</span>
              </div>
            )}
            
            <div className="flex items-center space-x-1">
              <Calendar className="h-4 w-4" />
              <span>Updated {formatDate(article.updated_at)}</span>
            </div>
            
            {article.read_count && (
              <div className="flex items-center space-x-1">
                <Eye className="h-4 w-4" />
                <span>{article.read_count} reads</span>
              </div>
            )}
          </div>
          
          {article.tags && article.tags.length > 0 && (
            <div className="flex items-center space-x-2 mt-3">
              <Tag className="h-4 w-4 text-gray-500" />
              <div className="flex flex-wrap gap-1">
                {article.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Article Content */}
      <Card>
        <CardContent className="pt-6">
          <div 
            className="prose prose-gray max-w-none"
            dangerouslySetInnerHTML={{ 
              __html: renderMarkdown(article.content) 
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
} 