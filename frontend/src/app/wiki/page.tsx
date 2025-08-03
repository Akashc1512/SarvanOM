"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Badge } from '@/ui/ui/badge';
import { Loader2, Plus, FileText, Calendar, User } from 'lucide-react';

interface WikiPage {
  id: string;
  title: string;
  summary: string;
  author?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
  read_count?: number;
}

export default function WikiHome() {
  const [wikiPages, setWikiPages] = useState<WikiPage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWikiPages();
  }, []);

  const fetchWikiPages = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/wiki');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setWikiPages(data);
    } catch (err) {
      console.error('Error fetching wiki pages:', err);
      setError(err instanceof Error ? err.message : 'Failed to load wiki pages');
      
      // Mock data for development/testing
      setWikiPages([
        {
          id: '1',
          title: 'Getting Started with SarvanOM',
          summary: 'Learn the basics of using the SarvanOM knowledge platform for your organization.',
          author: 'Admin',
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-20T14:30:00Z',
          tags: ['guide', 'beginner'],
          read_count: 156
        },
        {
          id: '2',
          title: 'Advanced Query Techniques',
          summary: 'Master advanced querying techniques to get the most out of your knowledge base.',
          author: 'Expert User',
          created_at: '2024-01-10T09:00:00Z',
          updated_at: '2024-01-18T16:45:00Z',
          tags: ['advanced', 'queries'],
          read_count: 89
        },
        {
          id: '3',
          title: 'API Integration Guide',
          summary: 'Complete guide for integrating SarvanOM APIs into your applications.',
          author: 'Developer',
          created_at: '2024-01-05T11:00:00Z',
          updated_at: '2024-01-12T13:20:00Z',
          tags: ['api', 'integration', 'technical'],
          read_count: 234
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading wiki pages...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              SarvanOM Knowledge Wiki
            </h1>
            <p className="text-gray-600">
              Explore and contribute to our comprehensive knowledge base
            </p>
          </div>
          <Link href="/wiki/new">
            <Button className="flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>New Article</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Wiki Pages Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {wikiPages.map((page) => (
          <Card key={page.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">
                  <Link 
                    href={`/wiki/${page.id}`}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    {page.title}
                  </Link>
                </CardTitle>
                <FileText className="h-5 w-5 text-gray-400" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4 line-clamp-3">
                {page.summary}
              </p>
              
              {/* Tags */}
              {page.tags && page.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {page.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
              
              {/* Meta Information */}
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-4">
                  {page.author && (
                    <div className="flex items-center space-x-1">
                      <User className="h-3 w-3" />
                      <span>{page.author}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(page.updated_at)}</span>
                  </div>
                </div>
                {page.read_count && (
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {page.read_count} reads
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {wikiPages.length === 0 && !error && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No wiki articles yet
          </h3>
          <p className="text-gray-600 mb-6">
            Be the first to create a wiki article and share your knowledge with the team.
          </p>
          <Link href="/wiki/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create First Article
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
} 