"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Input } from '@/ui/ui/input';
import { Label } from '@/ui/ui/label';
import { Textarea } from '@/ui/ui/textarea';
import { Badge } from '@/ui/ui/badge';
import { Alert, AlertDescription } from '@/ui/ui/alert';
import { Loader2, Save, ArrowLeft, Tag, X } from 'lucide-react';
import Link from 'next/link';

interface WikiArticle {
  title: string;
  content: string;
  summary: string;
  tags: string[];
}

export default function NewWikiPage() {
  const router = useRouter();
  const [article, setArticle] = useState<WikiArticle>({
    title: '',
    content: '',
    summary: '',
    tags: []
  });
  const [newTag, setNewTag] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleInputChange = (field: keyof WikiArticle, value: string) => {
    setArticle(prev => ({ ...prev, [field]: value }));
  };

  const addTag = () => {
    if (newTag.trim() && !article.tags.includes(newTag.trim())) {
      setArticle(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setArticle(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.target === e.currentTarget) {
      e.preventDefault();
      addTag();
    }
  };

  const handleSubmit = async () => {
    if (!article.title.trim() || !article.content.trim()) {
      setError('Title and content are required');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const response = await fetch('/api/wiki', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(article)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setSuccess(true);
      
      // Redirect to the new article after a short delay
      setTimeout(() => {
        router.push(`/wiki/${result.id}`);
      }, 1500);

    } catch (err) {
      console.error('Error creating wiki article:', err);
      setError(err instanceof Error ? err.message : 'Failed to create article');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/wiki" className="flex items-center text-blue-600 hover:text-blue-800 mb-2">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Wiki
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">
              Create New Wiki Article
            </h1>
            <p className="text-gray-600 mt-2">
              Share your knowledge with the team by creating a comprehensive wiki article.
            </p>
          </div>
        </div>
      </div>

      {/* Success Message */}
      {success && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <AlertDescription className="text-green-800">
            Article created successfully! Redirecting to the article...
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-6">
        {/* Title */}
        <Card>
          <CardHeader>
            <CardTitle>Article Title</CardTitle>
          </CardHeader>
          <CardContent>
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={article.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="Enter a descriptive title for your article..."
              className="mt-2"
            />
          </CardContent>
        </Card>

        {/* Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <Label htmlFor="summary">Brief Description</Label>
            <Textarea
              id="summary"
              value={article.summary}
              onChange={(e) => handleInputChange('summary', e.target.value)}
              placeholder="Provide a brief summary of what this article covers..."
              className="mt-2"
              rows={3}
            />
          </CardContent>
        </Card>

        {/* Tags */}
        <Card>
          <CardHeader>
            <CardTitle>Tags</CardTitle>
          </CardHeader>
          <CardContent>
            <Label htmlFor="tags">Add Tags</Label>
            <div className="flex gap-2 mt-2">
              <Input
                id="tags"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter a tag and press Enter..."
                className="flex-1"
              />
              <Button 
                type="button" 
                variant="outline" 
                onClick={addTag}
                disabled={!newTag.trim()}
              >
                <Tag className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Display Tags */}
            {article.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {article.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Content */}
        <Card>
          <CardHeader>
            <CardTitle>Article Content</CardTitle>
          </CardHeader>
          <CardContent>
            <Label htmlFor="content">Content *</Label>
            <Textarea
              id="content"
              value={article.content}
              onChange={(e) => handleInputChange('content', e.target.value)}
              placeholder="Write your article content here. You can use Markdown formatting..."
              className="mt-2 font-mono"
              rows={20}
            />
            <p className="text-sm text-gray-500 mt-2">
              You can use Markdown formatting for rich text content.
            </p>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <Link href="/wiki">
            <Button variant="outline">
              Cancel
            </Button>
          </Link>
          <Button 
            onClick={handleSubmit}
            disabled={isSubmitting || !article.title.trim() || !article.content.trim()}
            className="flex items-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save Article</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 